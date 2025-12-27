import os
import cv2
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import UploadImageForm
from .models import CarImage
from .yolo_model import yolo_model


def upload_view(request):
    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)

        if form.is_valid():
            car = form.save()
            img_path = car.image.path

            # 1️⃣ YOLO inference
            results = yolo_model.predict(img_path, imgsz=640)
            r = results[0]

            # 2️⃣ Extraire label
            if r.boxes and len(r.boxes) > 0:
                box = r.boxes[0]
                class_id = int(box.cls[0])
                car.detected_label = r.names[class_id]

            # 3️⃣ Générer image annotée
            annotated_img = r.plot()

            results_dir = Path(settings.MEDIA_ROOT) / "results"
            results_dir.mkdir(exist_ok=True)

            out_name = f"annotated_{car.pk}.jpg"
            out_path = results_dir / out_name

            cv2.imwrite(str(out_path), annotated_img)

            car.result_image.name = f"results/{out_name}"
            car.save()

            return redirect("result", pk=car.pk)

    else:
        form = UploadImageForm()

    return render(request, "upload.html", {"form": form})


def result_view(request, pk):
    car = get_object_or_404(CarImage, pk=pk)
    return render(request, "result.html", {"car": car})
