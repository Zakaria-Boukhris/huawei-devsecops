from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Materiel, Site

@login_required
def gestion_stock(request):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé - Réservé aux administrateurs')
        return redirect('dashboard')

    materiels = Materiel.objects.all()
    return render(request, 'materiel/gestion_stock_simple.html', {'materiels': materiels})

@login_required
def ajouter_materiel(request):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé - Réservé aux administrateurs')
        return redirect('dashboard')

    if request.method == 'POST':
        nom = request.POST['nom']
        qte_dispo = request.POST['qte_dispo']
        description = request.POST['description']

        materiel = Materiel.objects.create(
            nom=nom,
            qte_dispo=qte_dispo,
            description=description
        )
        messages.success(request, 'Matériel ajouté avec succès')
        return redirect('gestion_stock')

    return render(request, 'materiel/ajouter_materiel.html')

@login_required
def modifier_materiel(request, materiel_id):
    materiel = get_object_or_404(Materiel, id=materiel_id)

    if request.method == 'POST':
        materiel.nom = request.POST['nom']
        materiel.qte_dispo = request.POST['qte_dispo']
        materiel.description = request.POST['description']
        materiel.save()
        messages.success(request, 'Matériel modifié avec succès')
        return redirect('gestion_stock')

    return render(request, 'materiel/modifier_materiel.html', {'materiel': materiel})

@login_required
def valider_materiel(request, materiel_id):
    # Vérifier que l'utilisateur est admin
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé - Réservé aux administrateurs')
        return redirect('dashboard')

    materiel = get_object_or_404(Materiel, id=materiel_id)

    # Validation directe
    materiel.statut_validation = 'VALIDE'
    materiel.date_validation = timezone.now()
    materiel.save()
    messages.success(request, f'Matériel "{materiel.nom}" validé avec succès')

    return redirect('gestion_stock')

@login_required
def supprimer_materiel(request, materiel_id):
    # Vérifier que l'utilisateur est admin
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé - Réservé aux administrateurs')
        return redirect('dashboard')

    materiel = get_object_or_404(Materiel, id=materiel_id)

    nom_materiel = materiel.nom
    materiel.delete()
    messages.success(request, f'Matériel "{nom_materiel}" supprimé avec succès')
    return redirect('gestion_stock')

@login_required
def liste_materiels_employe(request):
    materiels = Materiel.objects.all().order_by('nom')

    # Filtres de recherche
    search = request.GET.get('search')
    if search:
        materiels = materiels.filter(nom__icontains=search)

    stock_filter = request.GET.get('stock')
    if stock_filter == 'disponible':
        materiels = materiels.filter(qte_dispo__gt=0)
    elif stock_filter == 'rupture':
        materiels = materiels.filter(qte_dispo=0)

    # Statistiques
    total_materiels = Materiel.objects.count()
    materiels_disponibles_count = Materiel.objects.filter(qte_dispo__gt=0).count()
    materiels_rupture_count = Materiel.objects.filter(qte_dispo=0).count()

    context = {
        'materiels': materiels,
        'materiels_disponibles_count': materiels_disponibles_count,
        'materiels_rupture_count': materiels_rupture_count,
        'search': search,
        'stock_filter': stock_filter,
    }

    return render(request, 'materiel/liste_materiels_employe.html', context)

@login_required
def admin_gestion_materiels(request):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé - Réservé aux administrateurs')
        return redirect('dashboard')

    # Traitement des actions POST
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            # Ajouter un nouveau matériel
            nom = request.POST.get('nom')
            reference = request.POST.get('reference')
            qte_dispo = request.POST.get('qte_dispo')
            site_id = request.POST.get('site')
            description = request.POST.get('description')

            try:
                materiel = Materiel.objects.create(
                    nom=nom,
                    reference=reference or None,
                    qte_dispo=int(qte_dispo),
                    description=description or None
                )

                if site_id:
                    site = Site.objects.get(id=site_id)
                    materiel.site = site
                    materiel.save()

                messages.success(request, f'Matériel "{nom}" ajouté avec succès')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

        elif action == 'edit':
            # Modifier un matériel existant
            materiel_id = request.POST.get('materiel_id')
            try:
                materiel = Materiel.objects.get(id=materiel_id)
                materiel.nom = request.POST.get('nom')
                materiel.reference = request.POST.get('reference') or None
                materiel.qte_dispo = int(request.POST.get('qte_dispo'))
                materiel.description = request.POST.get('description') or None

                site_id = request.POST.get('site')
                if site_id:
                    materiel.site = Site.objects.get(id=site_id)
                else:
                    materiel.site = None

                materiel.save()
                messages.success(request, f'Matériel "{materiel.nom}" modifié avec succès')
            except Materiel.DoesNotExist:
                messages.error(request, 'Matériel introuvable')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')

        elif action == 'delete':
            # Supprimer un matériel
            materiel_id = request.POST.get('materiel_id')
            try:
                materiel = Materiel.objects.get(id=materiel_id)
                nom_materiel = materiel.nom
                materiel.delete()
                messages.success(request, f'Matériel "{nom_materiel}" supprimé avec succès')
            except Materiel.DoesNotExist:
                messages.error(request, 'Matériel introuvable')
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')

        return redirect('admin_gestion_materiels')

    materiels = Materiel.objects.all().order_by('nom')

    search = request.GET.get('search')
    if search:
        materiels = materiels.filter(nom__icontains=search)

    site_filter = request.GET.get('site')
    if site_filter:
        materiels = materiels.filter(site_id=site_filter)

    stock_filter = request.GET.get('stock')
    if stock_filter == 'rupture':
        materiels = materiels.filter(qte_dispo=0)
    elif stock_filter == 'faible':
        materiels = materiels.filter(qte_dispo__lte=5, qte_dispo__gt=0)
    elif stock_filter == 'disponible':
        materiels = materiels.filter(qte_dispo__gt=5)

    stats = {
        'total': Materiel.objects.count(),
        'disponibles': Materiel.objects.filter(qte_dispo__gt=0).count(),
        'rupture': Materiel.objects.filter(qte_dispo=0).count(),
        'faible_stock': Materiel.objects.filter(qte_dispo__lte=5, qte_dispo__gt=0).count(),
    }

    sites = Site.objects.all()

    context = {
        'materiels': materiels,
        'stats': stats,
        'sites': sites,
        'search': search,
        'site_filter': site_filter,
        'stock_filter': stock_filter,
    }

    return render(request, 'materiel/admin_gestion_materiels.html', context)

@login_required
def voir_materiels(request):
    """Vue pour les employés pour voir tous les matériels disponibles"""
    materiels = Materiel.objects.all().order_by('nom')

    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        materiels = materiels.filter(
            Q(nom__icontains=search_query) |
            Q(reference__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filtrage par stock
    stock_filter = request.GET.get('stock')
    if stock_filter == 'disponible':
        materiels = materiels.filter(qte_dispo__gt=10)
    elif stock_filter == 'faible':
        materiels = materiels.filter(qte_dispo__lte=10, qte_dispo__gt=0)
    elif stock_filter == 'rupture':
        materiels = materiels.filter(qte_dispo=0)

    # Filtrage par site
    site_filter = request.GET.get('site')
    if site_filter:
        materiels = materiels.filter(site_id=site_filter)

    # Statistiques
    all_materiels = Materiel.objects.all()
    disponibles_count = all_materiels.filter(qte_dispo__gt=10).count()
    faible_count = all_materiels.filter(qte_dispo__lte=10, qte_dispo__gt=0).count()
    rupture_count = all_materiels.filter(qte_dispo=0).count()

    # Sites pour le filtre
    sites = Site.objects.all().order_by('nom')

    context = {
        'materiels': materiels,
        'disponibles_count': disponibles_count,
        'faible_count': faible_count,
        'rupture_count': rupture_count,
        'sites': sites,
        'search_query': search_query,
        'stock_filter': stock_filter,
        'site_filter': site_filter,
    }

    return render(request, 'materiel/voir_materiels.html', context)
