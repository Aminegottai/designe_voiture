import os
from pathlib import Path

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CarUploadForm
from .models import CarDesign

IA_API_URL = getattr(settings, "IA_API_URL", "").rstrip("/")  # ex: "https://...ngrok..." (sans /generate)


def base_page(request):
    return render(request, "base.html")


@login_required
def upload_car(request):
    """
    Upload d'une image (champ original_image), envoi à l'API IA (/generate), sauvegarde du rendu,
    puis redirection vers la page de détail du design.
    """
    if request.method == "POST":
        form = CarUploadForm(request.POST, request.FILES)
        if form.is_valid():
            car_design = form.save(commit=False)
            car_design.user = request.user
            car_design.save()

            if not IA_API_URL:
                messages.error(request, "IA_API_URL n'est pas configuré dans settings.")
                return redirect("cars:car_detail", pk=car_design.pk)

            # Lire le fichier uploadé depuis le champ original_image
            file_field = car_design.original_image
            try:
                file_field.open("rb")
                file_bytes = file_field.read()
                content_type = getattr(file_field.file, "content_type", "application/octet-stream")
            except Exception as e:
                messages.error(request, f"Impossible de lire le fichier uploadé : {e}")
                return redirect("cars:car_detail", pk=car_design.pk)

            prompt = form.cleaned_data.get("prompt") or None
            files = {"file": (file_field.name, file_bytes, content_type)}
            data = {}
            if prompt:
                data["prompt"] = prompt

            # Appel à l'API IA
            try:
                r = requests.post(f"{IA_API_URL}/generate", files=files, data=data, timeout=120)
                r.raise_for_status()
            except Exception as e:
                messages.error(request, f"Erreur lors de l'appel IA : {e}")
                return redirect("cars:car_detail", pk=car_design.pk)

            # Sauvegarder l'image générée
            gen_name = f"design_{car_design.pk}.png"
            car_design.generated_image.save(gen_name, ContentFile(r.content), save=True)

            messages.success(request, "Image uploadée et rendu IA généré avec succès !")
            return redirect("cars:car_detail", pk=car_design.pk)
    else:
        form = CarUploadForm()

    return render(request, "upload.html", {"form": form})


def car_detail(request, pk):
    design = get_object_or_404(CarDesign, pk=pk)
    return render(request, "detail.html", {"design": design})


@login_required
def import_latest_generated(request, pk):
    design = get_object_or_404(CarDesign, pk=pk)
    if design.user != request.user:
        messages.error(request, "Vous ne pouvez pas modifier ce design.")
        return redirect("cars:car_detail", pk=pk)

    folder = settings.COLAB_GENERATED_DIR
    if not os.path.isdir(folder):
        messages.error(request, f"Le dossier {folder} n'existe pas sur votre PC.")
        return redirect("cars:car_detail", pk=pk)

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".png")
    ]
    if not files:
        messages.error(request, "Aucune image générée trouvée dans le dossier.")
        return redirect("cars:car_detail", pk=pk)

    latest_file = max(files, os.path.getmtime)
    with open(latest_file, "rb") as f:
        png_bytes = f.read()

    filename = f"design_{design.id}_{Path(latest_file).name}"
    design.generated_image.save(filename, ContentFile(png_bytes), save=True)

    messages.success(request, f"Image IA importée depuis {Path(latest_file).name} !")
    return redirect("cars:car_detail", pk=pk)


def home(request):
    designs = CarDesign.objects.all().order_by("-created_at")[:8]
    return render(request, "home.html", {"designs": designs})

from django.utils.timezone import localtime
from django.db.models import Count
from datetime import datetime

def base_page(request):
    # Derniers designs (avec image générée si dispo)
    designs = CarDesign.objects.order_by("-created_at")[:8]

    renders = []
    for d in designs:
        renders.append({
            "title": d.title if hasattr(d, "title") else f"Design #{d.pk}",
            "status": "Terminé" if d.generated_image else "En cours",
            "age": localtime(d.created_at).strftime("%d/%m/%Y %H:%M"),
            "thumbnail_url": d.generated_image.url if d.generated_image else d.original_image.url if d.original_image else "",
            "detail_url": f"/cars/design/{d.pk}/",
            "duplicate_url": f"/cars/design/{d.pk}/duplicate",  # adapte si pas de route
            "download_url": d.generated_image.url if d.generated_image else "",
        })

    # Stats simples
    total = CarDesign.objects.count()
    processing = CarDesign.objects.filter(generated_image="").count()
    last = designs[0].created_at if designs else None

    context = {
        "hero_title": "Vos derniers rendus",
        "hero_subtitle": "Importez, générez et visualisez vos designs IA.",
        "stats": {
            "total": total,
            "processing": processing,
            "last_render": localtime(last).strftime("%d/%m/%Y %H:%M") if last else "-",
            "storage": "-",  # à calculer si besoin
        },
        "renders": renders,
        "activity": [
            f"• Nouveau rendu #{d.pk} — {localtime(d.created_at).strftime('%d/%m/%Y %H:%M')}"
            for d in designs
        ][:5],
        "templates": [
            {"name": "Sport", "description": "Lignes agressives, contrastes élevés.", "action_url": "/renders/new?template=sport"},
            {"name": "Luxe", "description": "Finitions premium, palette profonde.", "action_url": "/renders/new?template=luxe"},
            {"name": "Minimal", "description": "Silhouettes épurées, teintes sobres.", "action_url": "/renders/new?template=minimal"},
            {"name": "Corporate", "description": "Look pro, palette institutionnelle.", "action_url": "/renders/new?template=corporate"},
        ],
    }
    return render(request, "base.html", context)
    from django.contrib.auth.decorators import login_required

from django.urls import reverse

@login_required
def render_new(request):
    template = request.GET.get("template", "")
    # redirige vers upload en gardant le paramètre template
    target = reverse("cars:upload")
    if template:
        return redirect(f"{target}?template={template}")
    return redirect(target)