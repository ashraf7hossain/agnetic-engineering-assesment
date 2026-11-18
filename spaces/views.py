from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import SpaceForm, TestimonialForm
from .models import Space, Testimonial


def home(request):
    if request.user.is_authenticated:
        return redirect("spaces:dashboard")
    return render(request, "spaces/home.html")


@login_required
def dashboard(request):
    spaces = Space.objects.filter(owner=request.user).prefetch_related("testimonials")
    return render(request, "spaces/dashboard.html", {"spaces": spaces})


@login_required
def space_create(request):
    if request.method == "POST":
        form = SpaceForm(request.POST)
        if form.is_valid():
            space = form.save(commit=False)
            space.owner = request.user
            space.save()
            messages.success(request, "Space created.")
            return redirect("spaces:detail", slug=space.slug)
    else:
        form = SpaceForm()
    return render(request, "spaces/space_form.html", {"form": form, "mode": "create"})


def _owned_space(request, slug: str) -> Space | HttpResponseForbidden:
    space = get_object_or_404(Space, slug=slug)
    if space.owner_id != request.user.id:
        return HttpResponseForbidden("You do not own this space.")
    return space


@login_required
def space_detail(request, slug):
    space = _owned_space(request, slug)
    if isinstance(space, HttpResponseForbidden):
        return space
    counts = {
        "pending": space.testimonials.filter(status=Testimonial.Status.PENDING).count(),
        "approved": space.testimonials.filter(
            status=Testimonial.Status.APPROVED
        ).count(),
        "rejected": space.testimonials.filter(
            status=Testimonial.Status.REJECTED
        ).count(),
    }
    return render(
        request,
        "spaces/space_detail.html",
        {"space": space, "counts": counts},
    )


@login_required
def space_edit(request, slug):
    space = _owned_space(request, slug)
    if isinstance(space, HttpResponseForbidden):
        return space
    if request.method == "POST":
        form = SpaceForm(request.POST, instance=space)
        if form.is_valid():
            form.save()
            messages.success(request, "Space updated.")
            return redirect("spaces:detail", slug=space.slug)
    else:
        form = SpaceForm(instance=space)
    return render(
        request,
        "spaces/space_form.html",
        {"form": form, "mode": "edit", "space": space},
    )


@login_required
@require_POST
def space_delete(request, slug):
    space = _owned_space(request, slug)
    if isinstance(space, HttpResponseForbidden):
        return space
    space.delete()
    messages.success(request, "Space deleted.")
    return redirect("spaces:dashboard")


@login_required
def inbox(request, slug):
    space = _owned_space(request, slug)
    if isinstance(space, HttpResponseForbidden):
        return space
    status = request.GET.get("status", Testimonial.Status.PENDING)
    if status not in Testimonial.Status.values:
        status = Testimonial.Status.PENDING
    testimonials = space.testimonials.filter(status=status)
    return render(
        request,
        "spaces/inbox.html",
        {
            "space": space,
            "testimonials": testimonials,
            "status": status,
            "statuses": Testimonial.Status,
        },
    )


@login_required
@require_POST
def approve_testimonial(request, slug, pk):
    space = _owned_space(request, slug)
    if isinstance(space, HttpResponseForbidden):
        return space
    testimonial = get_object_or_404(Testimonial, pk=pk, space=space)
    testimonial.status = Testimonial.Status.APPROVED
    testimonial.save(update_fields=["status"])
    if request.headers.get("HX-Request"):
        return render(
            request,
            "spaces/partials/inbox_item.html",
            {"t": testimonial, "space": space, "just_updated": True},
        )
    messages.success(request, "Testimonial approved.")
    return redirect("spaces:inbox", slug=space.slug)


@login_required
@require_POST
def reject_testimonial(request, slug, pk):
    space = _owned_space(request, slug)
    if isinstance(space, HttpResponseForbidden):
        return space
    testimonial = get_object_or_404(Testimonial, pk=pk, space=space)
    testimonial.status = Testimonial.Status.REJECTED
    testimonial.save(update_fields=["status"])
    if request.headers.get("HX-Request"):
        return render(
            request,
            "spaces/partials/inbox_item.html",
            {"t": testimonial, "space": space, "just_updated": True},
        )
    messages.success(request, "Testimonial rejected.")
    return redirect("spaces:inbox", slug=space.slug)


def collect(request, slug):
    space = get_object_or_404(Space, slug=slug)
    form = TestimonialForm(space=space)
    return render(
        request,
        "spaces/collect.html",
        {"space": space, "form": form},
    )


@require_POST
def collect_submit(request, slug):
    space = get_object_or_404(Space, slug=slug)
    form = TestimonialForm(request.POST, space=space)
    if form.is_valid():
        testimonial = form.save(commit=False)
        testimonial.space = space
        testimonial.status = Testimonial.Status.PENDING
        if not space.collect_ratings:
            testimonial.rating = None
        testimonial.save()
        if request.headers.get("HX-Request"):
            return render(
                request,
                "spaces/partials/thank_you.html",
                {"space": space},
            )
        messages.success(request, "Thanks! Your testimonial was submitted.")
        return redirect("spaces:collect", slug=space.slug)
    if request.headers.get("HX-Request"):
        return render(
            request,
            "spaces/partials/collect_form.html",
            {"space": space, "form": form},
            status=422,
        )
    return render(
        request,
        "spaces/collect.html",
        {"space": space, "form": form},
        status=400,
    )


def wall(request, slug):
    space = get_object_or_404(Space, slug=slug)
    testimonials = space.testimonials.filter(status=Testimonial.Status.APPROVED)
    return render(
        request,
        "spaces/wall.html",
        {"space": space, "testimonials": testimonials},
    )
