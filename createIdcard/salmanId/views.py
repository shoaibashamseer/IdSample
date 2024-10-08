import PyPDF2
from django.contrib.staticfiles import finders
from django.shortcuts import render, redirect
from .forms import IDCardForm
from PIL import Image, ImageDraw, ImageFont
from django.core.files.storage import default_storage
import os
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
from django.http import FileResponse, HttpResponse

def home(request):
    return render(request, 'base.html')
def generate_salman_id_card(request):
    if request.method == 'POST':
        form = IDCardForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            name = form.cleaned_data['Name']
            designation = form.cleaned_data['Designation']
            emp_id = form.cleaned_data['Emp_id']
            photo = form.cleaned_data['Photo']
            dob = form.cleaned_data['Dob']
            address = form.cleaned_data['Address']
            blood_group = form.cleaned_data['Blood_group']
            mobile = form.cleaned_data['Mobile']
            qr_code = form.cleaned_data['Qr_code']

            # Save the uploaded photo temporarily
            photo_path = default_storage.save(f'tmp/{photo.name}', photo)
            photo_full_path = os.path.join(default_storage.location, photo_path)

            qr_code_path = default_storage.save(f'tmp/{qr_code.name}', qr_code)
            qr_code_full_path = os.path.join(default_storage.location, qr_code_path)

            page1_path = finders.find('salmanId/images/id_Page1.jpg')
            page2_path = finders.find('salmanId/images/id_Page2.jpg')

            if page1_path and page2_path:
                page1 = Image.open(page1_path).convert("RGBA")
                page2 = Image.open(page2_path).convert("RGBA")
            else:
                raise FileNotFoundError('One or both of the ID card templates were not found.')

            user_photo = Image.open(photo_full_path).convert("RGBA")
            user_photo = user_photo.resize((300, 300), Image.Resampling.LANCZOS)

            mask = Image.new('L', (300, 300), 0)  #
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 300, 300), fill=305)

            circular_photo = Image.new("RGBA", (300, 300))
            circular_photo.paste(user_photo, (0, 0), mask)

            page1.paste(circular_photo, (175, 359), circular_photo)

            draw_page1 = ImageDraw.Draw(page1)
            font = ImageFont.truetype("arial.ttf", 26)

            name = name.upper()
            designation = designation.upper()
            name_position = (175, 680)
            designation_position = (175, 720)

            draw_page1.text(name_position, name, font=ImageFont.truetype("arialbd.ttf", 30), fill="black")
            draw_page1.text(designation_position, designation, font=font, fill="black")

            qr_code_image = Image.open(qr_code_full_path).convert("RGBA")
            qr_code_image = qr_code_image.resize((120, 120), Image.Resampling.LANCZOS)
            qr_code_position = (450, 650)

            page1.paste(qr_code_image, qr_code_position, qr_code_image)

            draw = ImageDraw.Draw(page2)
            draw.text((250, 618), f" {emp_id}", font=font, fill="black")
            draw.text((250, 650), f" {dob}", font=font, fill="black")
            draw.text((250, 680), f" {address}", font=font, fill="black")
            draw.text((250, 750), f" {blood_group}", font=font, fill="black")
            draw.text((250, 780), f" {mobile}", font=font, fill="black")

            output_file_page1 = os.path.join(settings.MEDIA_ROOT, f'{emp_id}_page1.png')
            output_file_page2 = os.path.join(settings.MEDIA_ROOT, f'{emp_id}_page2.png')
            page1.save(output_file_page1, 'PNG')
            page2.save(output_file_page2)

            template_pdf_path = finders.find('salmanId/images/sample1.pdf')
            with open(template_pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page = reader.pages[0]
                template_width = float(page.mediabox[2])
                template_height = float(page.mediabox[3])

            output_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{emp_id}_id_card.pdf')

            pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=(template_width, template_height))

            pdf_canvas.drawImage(output_file_page1, 0, 0, width=template_width, height=template_height)
            pdf_canvas.showPage()
            pdf_canvas.drawImage(output_file_page2, 0, 0, width=template_width, height=template_height)

            pdf_canvas.save()
            request.session['emp_id'] = emp_id
            request.session['front_image'] = f'{settings.MEDIA_URL}{emp_id}_page1.png'
            request.session['back_image'] = f'{settings.MEDIA_URL}{emp_id}_page2.png'

            os.remove(photo_full_path)

            return redirect('salman:success')
    else:
        form = IDCardForm()

    return render(request, 'generate_id_card.html', {'form': form})



'''def modified_id_card(request):
    return render_modified_id_card(request, 'salmanId')

def download_id_card_pdf(request, person_id):
    return handle_download_id_card_pdf(request, person_id)'''


def modified_id_card(request):
    front_image = request.session.get('front_image')
    back_image = request.session.get('back_image')
    emp_id = request.session.get('emp_id')

    return render(request, 'salmanId/success.html', {
        'front_image': front_image,
        'back_image': back_image,
        'emp_id': emp_id
    })


def download_id_card_pdf(request, emp_id):
    file_path = os.path.join(settings.MEDIA_ROOT, f'{emp_id}_id_card.pdf')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf', as_attachment=True,
                            filename=f'{emp_id}_id_card.pdf')
    else:
        return HttpResponse("File not found.", status=404)
