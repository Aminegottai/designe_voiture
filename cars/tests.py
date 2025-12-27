import os
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

            results = yolo_model.predict(img_path, imgsz=640)
            r = results[0]

            label = None
            if r.boxes and len(r.boxes) > 0:
                box = r.boxes[0]
                class_id = int(box.cls[0].cpu().numpy())
                label = r.names[class_id]
                car.detected_label = label

            temp_dir = Path(settings.MEDIA_ROOT) / "temp"
            temp_dir.mkdir(exist_ok=True)

            r.save(save_dir=temp_dir)

            annotated_file = None
            for f in temp_dir.glob("*"):
                if f.suffix.lower() in [".jpg", ".png"]:
                    annotated_file = f
                    break

            if annotated_file:
                final_dir = Path(settings.MEDIA_ROOT) / "results"
                final_dir.mkdir(exist_ok=True)
                dest = final_dir / annotated_file.name
                dest.write_bytes(annotated_file.read_bytes())

                car.result_image.name = "results/" + annotated_file.name
                car.save()

            return redirect("result", pk=car.pk)

    else:
        form = UploadImageForm()

    return render(request, "upload.html", {"form": form})

def result_view(request, pk):
    car = get_object_or_404(CarImage, pk=pk)
    return render(request, "result.html", {"car": car})
