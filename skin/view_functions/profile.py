from django.contrib import messages

from skin.models.profile import UserProfile, SkinProfile, Lifestyle, CurrentRoutine, Product
from skin.forms.profile_forms import SkinProfileForm, LifestyleForm, CurrentRoutineForm, ProductForm
from django.http import HttpResponse
from django.core.files.base import ContentFile as File
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect



@login_required
def overall_skin_profile_view(request):
    skin_profile, _ = SkinProfile.objects.get_or_create(user=request.user)
    lifestyle, _ = Lifestyle.objects.get_or_create(profile=skin_profile)
    current_routine, _ = CurrentRoutine.objects.get_or_create(profile=skin_profile)
    products = Product.objects.filter(profile=skin_profile)

    skin_profile_complete = skin_profile.completion_percentage
    lifestyle_complete = lifestyle.completion_percentage
    routine_complete = current_routine.completion_percentage
    if products.exists():
        products_complete = sum(
            product.completion_percentage for product in products
        ) / products.count()
    else:
        products_complete = 0


    profile_exists = (
        skin_profile.profile_exists or
        lifestyle.lifestyle_exists or
        current_routine.routine_exists or
        products.exists()
    )

    total_completion = round((skin_profile_complete + lifestyle_complete + routine_complete + products_complete) / 4)

    context = {
        'skin_profile': skin_profile,
        'lifestyle': lifestyle,
        'current_routine': current_routine,
        'products': products,

        'skin_profile_complete': skin_profile_complete,
        'lifestyle_complete': lifestyle_complete,
        'routine_complete': routine_complete,
        'products_complete': products_complete,

        'total_completion': total_completion,

        'skin_profile_exists': skin_profile.profile_exists,
        'lifestyle_exists': lifestyle.lifestyle_exists,
        'routine_exists': current_routine.routine_exists,
        'products_exist': products.exists(),
    }

    context['profile_exists'] = profile_exists

    return render(request, 'skin/skin_profile.html', context)








@login_required
def edit_skin_profile_view(request):
    skin_profile, _ = SkinProfile.objects.get_or_create(user=request.user)
    lifestyle, _ = Lifestyle.objects.get_or_create(profile=skin_profile)
    current_routine, _ = CurrentRoutine.objects.get_or_create(profile=skin_profile)
    products = Product.objects.filter(profile=skin_profile)

    skin_profile_form = SkinProfileForm(
        request.POST or None,
        instance=skin_profile
    )

    lifestyle_form = LifestyleForm(
        request.POST or None,
        instance=lifestyle
    )

    current_routine_form = CurrentRoutineForm(
        request.POST or None,
        instance=current_routine
    )

    product_form = ProductForm(request.POST or None)

    if request.method == "POST":
        if "save_basic" in request.POST:
            if skin_profile_form.is_valid():
                skin_profile_form.save()
                messages.success(
                    request,
                    "Basic information updated successfully."
                )
                return redirect("edit_skin_profile")

        elif "save_lifestyle" in request.POST:
            if lifestyle_form.is_valid():
                lifestyle_form.save()
                messages.success(
                    request,
                    "Lifestyle information updated successfully."
                )
                return redirect("edit_skin_profile")

        elif "save_routine" in request.POST:
            if current_routine_form.is_valid():
                current_routine_form.save()
                messages.success(
                    request,
                    "Routine information updated successfully."
                )
                return redirect("edit_skin_profile")

        elif "save_product" in request.POST:
            if product_form.is_valid():
                product = product_form.save(commit=False)
                product.profile = skin_profile
                product.save()

                messages.success(
                    request,
                    "Product added successfully."
                )

                return redirect("edit_skin_profile")

    skin_profile_complete = round(skin_profile.completion_percentage)
    lifestyle_complete = round(lifestyle.completion_percentage)
    routine_complete = round(current_routine.completion_percentage)

    if products.exists():
        products_complete = round(
            sum(
                product.completion_percentage
                for product in products
            ) / products.count()
        )
    else:
        products_complete = 0

    total_completion = round(
        (
            skin_profile_complete
            + lifestyle_complete
            + routine_complete
            + products_complete
        ) / 4
    )

    context = {
        'skin_profile': skin_profile,
        'lifestyle': lifestyle,
        'current_routine': current_routine,
        'products': products,

        'product_form': product_form,
        'skin_profile_form': skin_profile_form,
        'lifestyle_form': lifestyle_form,
        'current_routine_form': current_routine_form,

        # Completion
        'skin_profile_complete': skin_profile_complete,
        'lifestyle_complete': lifestyle_complete,
        'routine_complete': routine_complete,
        'products_complete': products_complete,
        'total_completion': total_completion,
    }

    return render(
        request,
        'skin/edit_skin_profile.html',
        context
    )





