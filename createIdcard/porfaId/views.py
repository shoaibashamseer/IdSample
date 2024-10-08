import PyPDF2
from django.contrib.staticfiles import finders
from django.shortcuts import render, redirect
from .forms import IDCardForm
from PIL import Image, ImageDraw, ImageFont
from django.core.files.storage import default_storage
import os
from .models import PorfaIDCard
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
from django.http import FileResponse, HttpResponse
from .models import PorfaIDCard
from django.db import IntegrityError


def generate_porfa_id_card(request):
    if request.method == 'POST':
        form = IDCardForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                name = form.cleaned_data['name']
                designation = form.cleaned_data['designation']
                photo = form.cleaned_data['photo']
                patient_address = form.cleaned_data['patient_address']
                blood_group = form.cleaned_data['blood_group']
                mobile = form.cleaned_data['mobile']
                emergency = form.cleaned_data['emergency']
                qr_code = form.cleaned_data['qr_code']
                ration_card = form.cleaned_data['ration_card']
                treatment_type = form.cleaned_data['treatment_type']

                porfa_id, last_number = PorfaIDCard.generate_porfa_id(treatment_type)

                if PorfaIDCard.objects.filter(porfa_id=porfa_id).exists():
                    raise IntegrityError(f'Porfa ID {porfa_id} already exists.')

                porfa_id_card = PorfaIDCard(
                    name=name,
                    designation=designation,
                    photo=photo,
                    patient_address=patient_address,
                    blood_group=blood_group,
                    mobile=mobile,
                    emergency=emergency,
                    qr_code=qr_code,
                    ration_card=ration_card,
                    treatment_type=treatment_type,
                    porfa_id=porfa_id,
                    last_number=last_number
                )

                porfa_id_card.save()

                # Save the uploaded photo temporarily
                photo_path = default_storage.save(f'tmp/{photo.name}', photo)
                photo_full_path = os.path.join(default_storage.location, photo_path)

                qr_code_path = default_storage.save(f'tmp/{qr_code.name}', qr_code)
                qr_code_full_path = os.path.join(default_storage.location, qr_code_path)

                page1_path = finders.find('PorfaId/images/porfa_Page1.png')
                page2_path = finders.find('PorfaId/images/porfa_Page2.png')

                if page1_path and page2_path:
                    page1 = Image.open(page1_path).convert("RGBA")
                    page2 = Image.open(page2_path).convert("RGBA")
                else:
                    raise FileNotFoundError('One or both of the ID card templates were not found.')

                user_photo = Image.open(photo_full_path).convert("RGBA")
                user_photo = user_photo.resize((300, 300), Image.Resampling.LANCZOS)

                hex_mask = Image.new('L', (300, 300), 0)
                draw = ImageDraw.Draw(hex_mask)
                hexagon_vertices = [
                    (150, 0), (300, 75), (300, 225), (150, 300), (0, 225), (0, 75)
                ]
                draw.polygon(hexagon_vertices, fill=255)

                hex_photo = Image.new("RGBA", (300, 300))
                hex_photo.paste(user_photo, (0, 0), hex_mask)

                page1.paste(hex_photo, (175, 359), hex_photo)

                draw_page1 = ImageDraw.Draw(page1)
                font = ImageFont.truetype("arialbd.ttf", 26)

                name = name.upper()
                designation = designation.upper()
                name_position = (250, 680)
                designation_position = (250, 750)
                treatment_type = treatment_type.upper()

                draw_page1.text(name_position, name, font=ImageFont.truetype("arialbd.ttf", 30), fill="black")
                draw_page1.text((300, 680), f" {porfa_id}", font=font, fill="black")
                draw_page1.text(designation_position, designation, font=font, fill="black")
                draw_page1.text((250, 850), f" {treatment_type}", font=font, fill="black")

                qr_code_image = Image.open(qr_code_full_path).convert("RGBA")
                qr_code_image = qr_code_image.resize((110, 110), Image.Resampling.LANCZOS)
                qr_code_position1 = (50, 780)

                page1.paste(qr_code_image, qr_code_position1, qr_code_image)

                draw = ImageDraw.Draw(page2)
                qr_code_position2 = (60, 28)
                draw.text((250, 212), f" {porfa_id}", font=font, fill="black")
                draw.text((380, 310), f" {patient_address}", font=font, fill="black")
                draw.text((380, 520), f" {mobile}", font=font, fill="black")
                draw.text((380, 570), f" {emergency}", font=font, fill="black")
                draw.text((380, 620), f" {blood_group}", font=font, fill="black")
                draw.text((380, 680), f" {ration_card}", font=font, fill="black")

                page2.paste(qr_code_image, qr_code_position2, qr_code_image)

                output_file_page1 = os.path.join(settings.MEDIA_ROOT, f'{porfa_id}_page1.png')
                output_file_page2 = os.path.join(settings.MEDIA_ROOT, f'{porfa_id}_page2.png')
                page1.save(output_file_page1, 'PNG')
                page2.save(output_file_page2)

                template_pdf_path = finders.find('porfaId/images/porfasample.pdf')
                with open(template_pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    page = reader.pages[0]
                    template_width = float(page.mediabox[2])
                    template_height = float(page.mediabox[3])

                output_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{porfa_id}_id_card.pdf')

                pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=(template_width, template_height))

                pdf_canvas.drawImage(output_file_page1, 0, 0, width=template_width, height=template_height)
                pdf_canvas.showPage()
                pdf_canvas.drawImage(output_file_page2, 0, 0, width=template_width, height=template_height)

                pdf_canvas.save()

                request.session['porfa_id'] = porfa_id
                request.session['front_image'] = f'{settings.MEDIA_URL}{porfa_id}_page1.png'
                request.session['back_image'] = f'{settings.MEDIA_URL}{porfa_id}_page2.png'

                os.remove(photo_full_path)

                return redirect('porfa:success')

            except IntegrityError as e:
                form.add_error(None, str(e))
    else:
        form = IDCardForm()

    return render(request, 'generate_id_card.html', {'form': form})


def modified_id_card(request):
    front_image = request.session.get('front_image')
    back_image = request.session.get('back_image')
    porfa_id = request.session.get('porfa_id')

    return render(request, 'porfaId/success.html', {
        'front_image': front_image,
        'back_image': back_image,
        'porfa_id': porfa_id
    })


def download_id_card_pdf(request, porfa_id):
    file_path = os.path.join(settings.MEDIA_ROOT, f'{porfa_id}_id_card.pdf')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf', as_attachment=True,
                            filename=f'{porfa_id}_id_card.pdf')
    else:
        return HttpResponse("File not found.", status=404)
