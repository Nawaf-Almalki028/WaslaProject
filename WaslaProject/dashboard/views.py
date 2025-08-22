from django.shortcuts import render, redirect, error404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import Hackathon, Participant, Team, Submission
from .forms import HackathonForm, ParticipantRegistrationForm, TeamForm, SubmissionForm


class HackathonListView(ListView):
    model = Hackathon
    template_name = 'hackathons/list.html'
    context_object_name = 'hackathons'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Hackathon.objects.filter(status='active')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city=city)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        time_filter = self.request.GET.get('time')
        if time_filter == 'upcoming':
            queryset = queryset.filter(start_date__gt=timezone.now())
        elif time_filter == 'ongoing':
            now = timezone.now()
            queryset = queryset.filter(
                start_date__lte=now,
                end_date__gte=now
            )
        
        ordering = self.request.GET.get('ordering', '-start_date')
        queryset = queryset.order_by(ordering)
        
        return queryset.select_related('organizer').annotate(
            participant_count=Count('participants')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = Hackathon.CITY_CHOICES
        context['selected_city'] = self.request.GET.get('city', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['title'] = 'Hackathons - WASLA'
        return context


class HackathonDetailView(DetailView):
    model = Hackathon
    template_name = 'hackathons/detail.html'
    context_object_name = 'hackathon'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hackathon = self.object
        user = self.request.user
        
        context['is_registered'] = False
        context['user_team'] = None
        
        if user.is_authenticated:
            try:
                participant = Participant.objects.get(
                    hackathon=hackathon,
                    user=user
                )
                context['is_registered'] = True
                context['user_team'] = participant.team
            except Participant.DoesNotExist:
                pass
        
        context['teams'] = hackathon.teams.annotate(
            member_count=Count('members')
        )
        context['recent_submissions'] = hackathon.submissions.select_related(
            'team', 'participant'
        )[:5]
        return context


class HackathonCreateView(LoginRequiredMixin, CreateView):
    model = Hackathon
    form_class = HackathonForm
    template_name = 'hackathons/create.html'
    
    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, 'Hackathon created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('hackathons:detail', kwargs={'slug': self.object.slug})


@login_required
def register_for_hackathon(request, slug):
    hackathon = error404(Hackathon, slug=slug)
    
    if not hackathon.is_registration_open:
        messages.error(request, 'Registration is closed for this hackathon.')
        return redirect('hackathons:detail', slug=slug)
    
    if Participant.objects.filter(hackathon=hackathon, user=request.user).exists():
        messages.info(request, 'You are already registered for this hackathon.')
        return redirect('hackathons:detail', slug=slug)
    
    if request.method == 'POST':
        form = ParticipantRegistrationForm(request.POST, hackathon=hackathon)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.hackathon = hackathon
            participant.user = request.user
            participant.save()
            
            messages.success(
                request,
                f'Successfully registered for {hackathon.title}!'
            )
            return redirect('hackathons:detail', slug=slug)
    else:
        form = ParticipantRegistrationForm(hackathon=hackathon)
    
    return render(request, 'hackathons/register.html', {
        'form': form,
        'hackathon': hackathon,
        'title': f'Register for {hackathon.title}'
    })


@login_required
def dashboard_view(request):
    user = request.user
    
    my_hackathons = Hackathon.objects.filter(
        organizer=user
    ).annotate(
        participant_count=Count('participants'),
        submission_count=Count('submissions')
    ).order_by('-created_at')[:3]
    
    my_participations = Participant.objects.filter(
        user=user
    ).select_related('hackathon', 'team').order_by('-registered_at')[:5]
    
    upcoming_hackathons = Hackathon.objects.filter(
        status='active',
        start_date__gt=timezone.now()
    ).exclude(
        participants__user=user
    ).order_by('start_date')[:4]
    
    subscription = None
    if hasattr(user, 'subscriptions'):
        subscription = user.subscriptions.filter(
            status='active'
        ).select_related('plan').first()
    
    context = {
        'my_hackathons': my_hackathons,
        'my_participations': my_participations,
        'upcoming_hackathons': upcoming_hackathons,
        'subscription': subscription,
        'title': 'Dashboard - WASLA'
    }
    
    return render(request, 'hackathons/dashboard.html', context)