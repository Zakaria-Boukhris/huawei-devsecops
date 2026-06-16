from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Demande
from materiel.models import Materiel, Site
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

@login_required
def creer_demande(request):
    if request.method == 'POST':
        qte = request.POST.get('qte')
        description = request.POST.get('description')
        site_id = request.POST.get('site')
        materiel_ids = request.POST.getlist('materiel')

        # Validation
        if not qte or not description or not site_id or not materiel_ids:
            messages.error(request, 'Tous les champs obligatoires doivent être remplis')
            materiels = Materiel.objects.all()
            sites = Site.objects.all()
            return render(request, 'demandes/creer_demande_simple.html', {
                'materiels': materiels,
                'sites': sites
            })

        if len(description) < 20:
            messages.error(request, 'La description doit contenir au moins 20 caractères')
            materiels = Materiel.objects.all()
            sites = Site.objects.all()
            return render(request, 'demandes/creer_demande_simple.html', {
                'materiels': materiels,
                'sites': sites
            })

        try:
            site = Site.objects.get(id=site_id)

            demande = Demande.objects.create(
                qte=int(qte),
                description=description,
                site=site,
                employee=request.user
            )
            demande.materiel.set(materiel_ids)

            messages.success(request, f'Demande #{demande.id} créée avec succès pour le site {site.nom}')
            return redirect('consulter_demandes')

        except Site.DoesNotExist:
            messages.error(request, 'Site sélectionné invalide')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')

    materiels = Materiel.objects.filter(qte_dispo__gt=0).order_by('nom')
    sites = Site.objects.all().order_by('nom')

    # Si un matériel est pré-sélectionné via URL
    selected_materiel = request.GET.get('materiel')

    return render(request, 'demandes/creer_demande_simple.html', {
        'materiels': materiels,
        'sites': sites,
        'selected_materiel': selected_materiel
    })

@login_required
def consulter_demandes(request):
    if request.user.is_admin:
        # Admin voit toutes les demandes pour validation
        demandes = Demande.objects.all().order_by('-date_dmd')

        # Statistiques pour admin
        en_attente_count = demandes.filter(statuts='EN_ATTENTE').count()
        validees_count = demandes.filter(statuts='VALIDEE').count()
        refusees_count = demandes.filter(statuts='REFUSEE').count()

        # Filtrage par statut si demandé
        statut_filter = request.GET.get('statut')
        if statut_filter:
            demandes = demandes.filter(statuts=statut_filter)

        # Recherche si demandée
        search = request.GET.get('search')
        if search:
            demandes = demandes.filter(id__icontains=search)

        context = {
            'demandes': demandes,
            'en_attente_count': en_attente_count,
            'validees_count': validees_count,
            'refusees_count': refusees_count,
        }
        return render(request, 'demandes/consulter_demandes_simple.html', context)
    else:
        # Employé voit seulement ses demandes
        demandes = Demande.objects.filter(employee=request.user).order_by('-date_dmd')

        # Filtrage par statut
        statut_filter = request.GET.get('statut')
        if statut_filter:
            demandes = demandes.filter(statuts=statut_filter)

        # Statistiques pour employé (sur toutes ses demandes)
        all_demandes = Demande.objects.filter(employee=request.user)
        en_attente_count = all_demandes.filter(statuts='EN_ATTENTE').count()
        validees_count = all_demandes.filter(statuts='VALIDEE').count()
        refusees_count = all_demandes.filter(statuts='REFUSEE').count()

        # Notifications pour demandes récentes (dernières 7 jours)
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=7)

        demandes_validees_recentes = all_demandes.filter(
            statuts='VALIDEE',
            date_validation__gte=recent_date
        ).count()

        demandes_refusees_recentes = all_demandes.filter(
            statuts='REFUSEE',
            date_validation__gte=recent_date
        ).count()

        # Notifications détaillées pour le panneau
        recent_notifications = all_demandes.filter(
            Q(statuts='VALIDEE', date_validation__gte=recent_date) |
            Q(statuts='REFUSEE', date_validation__gte=recent_date) |
            Q(statuts='EN_ATTENTE', date_dmd__gte=recent_date)
        ).order_by('-date_dmd')[:10]  # Limiter à 10 notifications récentes

        notifications_count = recent_notifications.count()

        context = {
            'demandes': demandes,
            'en_attente_count': en_attente_count,
            'validees_count': validees_count,
            'refusees_count': refusees_count,
            'statut_filter': statut_filter,
            'demandes_validees_recentes': demandes_validees_recentes,
            'demandes_refusees_recentes': demandes_refusees_recentes,
            'recent_notifications': recent_notifications,
            'notifications_count': notifications_count,
        }

        return render(request, 'demandes/consulter_demandes.html', context)

@login_required
def valider_demande(request, demande_id):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé')
        return redirect('consulter_demandes')

    demande = get_object_or_404(Demande, id=demande_id)

    # Validation directe - on valide automatiquement
    demande.statuts = 'VALIDEE'
    demande.admin = request.user
    demande.date_validation = timezone.now()  # Enregistrer la date de validation
    demande.save()
    messages.success(request, f'Demande #{demande_id} validée avec succès')

    return redirect('consulter_demandes')

@login_required
def refuser_demande(request, demande_id):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé')
        return redirect('consulter_demandes')

    demande = get_object_or_404(Demande, id=demande_id)

    # Refus direct
    demande.statuts = 'REFUSEE'
    demande.admin = request.user
    demande.date_validation = timezone.now()  # Utiliser le même champ pour la date de refus
    demande.save()
    messages.warning(request, f'Demande #{demande_id} refusée')

    return redirect('consulter_demandes')

@login_required
def supprimer_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    # Vérifier que l'utilisateur peut supprimer cette demande
    if demande.employee != request.user and not request.user.is_admin:
        messages.error(request, 'Accès non autorisé')
        return redirect('consulter_demandes')

    # Suppression directe (la confirmation se fait côté JavaScript)
    demande.delete()
    messages.success(request, f'Demande #{demande_id} supprimée avec succès')
    return redirect('consulter_demandes')

@login_required
def admin_gestion_demandes(request):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé - Réservé aux administrateurs')
        return redirect('dashboard')

    # Traitement des actions POST
    if request.method == 'POST':
        demande_id = request.POST.get('demande_id')
        action = request.POST.get('action')

        try:
            demande = Demande.objects.get(id=demande_id)

            if action == 'valider':
                demande.statuts = 'VALIDEE'
                demande.admin = request.user
                demande.date_validation = timezone.now()
                demande.save()
                messages.success(request, f'Demande #{demande_id} validée avec succès')

            elif action == 'refuser':
                demande.statuts = 'REFUSEE'
                demande.admin = request.user
                demande.date_validation = timezone.now()
                demande.save()
                messages.warning(request, f'Demande #{demande_id} refusée')

            elif action == 'attente':
                demande.statuts = 'EN_ATTENTE'
                demande.admin = None
                demande.date_validation = None
                demande.save()
                messages.info(request, f'Demande #{demande_id} remise en attente')

        except Demande.DoesNotExist:
            messages.error(request, 'Demande introuvable')

        return redirect('admin_gestion_demandes')

    demandes = Demande.objects.all().order_by('-date_dmd')

    statut_filter = request.GET.get('statut')
    if statut_filter:
        demandes = demandes.filter(statuts=statut_filter)

    search = request.GET.get('search')
    if search:
        demandes = demandes.filter(
            employee__email__icontains=search
        ) | demandes.filter(
            id__icontains=search
        )

    stats = {
        'total': Demande.objects.count(),
        'en_attente': Demande.objects.filter(statuts='EN_ATTENTE').count(),
        'validees': Demande.objects.filter(statuts='VALIDEE').count(),
        'refusees': Demande.objects.filter(statuts='REFUSEE').count(),
    }

    context = {
        'demandes': demandes,
        'stats': stats,
        'statut_filter': statut_filter,
        'search': search,
    }

    return render(request, 'demandes/admin_gestion_demandes.html', context)

@login_required
def admin_traiter_demande(request, demande_id):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé')
        return redirect('dashboard')

    demande = get_object_or_404(Demande, id=demande_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        commentaire = request.POST.get('commentaire', '')

        if action == 'valider':
            demande.statuts = 'VALIDEE'
            demande.date_validation = timezone.now()
            demande.commentaire_admin = commentaire
            demande.save()

            messages.success(request, f'Demande #{demande_id} validée avec succès')

        elif action == 'refuser':
            demande.statuts = 'REFUSEE'
            demande.date_validation = timezone.now()
            demande.commentaire_admin = commentaire
            demande.save()

            messages.success(request, f'Demande #{demande_id} refusée')

        elif action == 'attente':
            demande.statuts = 'EN_ATTENTE'
            demande.commentaire_admin = commentaire
            demande.save()

            messages.info(request, f'Demande #{demande_id} remise en attente')

        return redirect('admin_gestion_demandes')

    context = {
        'demande': demande,
    }

    return render(request, 'demandes/admin_traiter_demande.html', context)
