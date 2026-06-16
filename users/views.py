from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect')
    return render(request, 'users/login_simple.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Redirection selon le rôle de l'utilisateur
    if request.user.is_admin:
        return dashboard_admin(request)
    else:
        return dashboard_employe(request)

@login_required
def dashboard_employe(request):
    from demandes.models import Demande
    from materiel.models import Materiel

    # Statistiques pour l'employé connecté
    mes_demandes = Demande.objects.filter(employee=request.user)
    mes_demandes_count = mes_demandes.count()
    demandes_en_attente = mes_demandes.filter(statuts='EN_ATTENTE').count()
    demandes_validees = mes_demandes.filter(statuts='VALIDEE').count()
    demandes_refusees = mes_demandes.filter(statuts='REFUSEE').count()

    # Dernières demandes de l'employé
    dernieres_demandes = mes_demandes.order_by('-date_dmd')[:5]

    # Matériels disponibles (aperçu)
    materiels_disponibles = Materiel.objects.filter(qte_dispo__gt=0).order_by('-qte_dispo')[:12]

    context = {
        'mes_demandes_count': mes_demandes_count,
        'demandes_en_attente': demandes_en_attente,
        'demandes_validees': demandes_validees,
        'demandes_refusees': demandes_refusees,
        'dernieres_demandes': dernieres_demandes,
        'materiels_disponibles': materiels_disponibles,
    }

    return render(request, 'users/dashboard_employe.html', context)

@login_required
def ajouter_employe(request):
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé - Réservé aux administrateurs')
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action', 'create')

        if action == 'create':
            # Créer un nouvel employé
            email = request.POST.get('email')
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            password = request.POST.get('password')
            site_id = request.POST.get('site')

            # Validation
            if not all([email, nom, prenom, password]):
                messages.error(request, 'Tous les champs sont obligatoires')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Un utilisateur avec cet email existe déjà')
            elif len(password) < 6:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères')
            else:
                try:
                    # Créer l'utilisateur
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        nom=nom,
                        prenom=prenom,
                        is_employee=True,
                        is_admin=False
                    )

                    # Assigner le site si fourni
                    if site_id:
                        from materiel.models import Site
                        try:
                            site = Site.objects.get(id=site_id)
                            user.site = site
                            user.save()
                        except Site.DoesNotExist:
                            pass

                    messages.success(request, f'Employé {prenom} {nom} créé avec succès!')
                    return redirect('ajouter_employe')

                except Exception as e:
                    messages.error(request, f'Erreur lors de la création: {str(e)}')

        elif action == 'edit':
            # Modifier un employé existant
            employe_id = request.POST.get('employe_id')
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            email = request.POST.get('email')

            try:
                employe = User.objects.get(id=employe_id, is_employee=True)

                # Vérifier si l'email n'est pas déjà utilisé par un autre utilisateur
                if User.objects.filter(email=email).exclude(id=employe_id).exists():
                    messages.error(request, 'Un utilisateur avec cet email existe déjà')
                else:
                    employe.nom = nom
                    employe.prenom = prenom
                    employe.email = email
                    employe.username = email
                    employe.save()

                    messages.success(request, f'Employé {prenom} {nom} modifié avec succès!')
                    return redirect('ajouter_employe')

            except User.DoesNotExist:
                messages.error(request, 'Employé introuvable')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')

        elif action == 'delete':
            # Supprimer un employé
            employe_id = request.POST.get('employe_id')

            try:
                employe = User.objects.get(id=employe_id, is_employee=True)
                nom_complet = f"{employe.prenom} {employe.nom}"
                employe.delete()

                messages.success(request, f'Employé {nom_complet} supprimé avec succès!')
                return redirect('ajouter_employe')

            except User.DoesNotExist:
                messages.error(request, 'Employé introuvable')
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    # Récupérer les sites pour le formulaire
    from materiel.models import Site
    sites = Site.objects.all()

    # Statistiques des employés
    total_employes = User.objects.filter(is_employee=True).count()
    employes_recents = User.objects.filter(is_employee=True).order_by('-date_joined')[:5]
    all_employes = User.objects.filter(is_employee=True).order_by('-date_joined')

    context = {
        'sites': sites,
        'total_employes': total_employes,
        'employes_recents': employes_recents,
        'all_employes': all_employes,
    }

    return render(request, 'users/ajouter_employe.html', context)

@login_required
def dashboard_admin(request):
    from demandes.models import Demande
    from materiel.models import Materiel
    from datetime import datetime, timedelta

    # Vérifier que l'utilisateur est admin
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé')
        return redirect('dashboard')

    # Statistiques globales
    total_demandes = Demande.objects.count()
    total_materiels = Materiel.objects.count()
    total_users = User.objects.count()

    # Demandes en attente globales
    demandes_en_attente_global = Demande.objects.filter(statuts='EN_ATTENTE').count()
    demandes_en_attente = Demande.objects.filter(statuts='EN_ATTENTE').order_by('-date_dmd')[:10]

    # Statistiques de validation
    demandes_validees_total = Demande.objects.filter(statuts='VALIDEE').count()
    demandes_refusees_total = Demande.objects.filter(statuts='REFUSEE').count()

    # Matériels en stock critique (moins de 5 unités)
    materiels_critiques = Materiel.objects.filter(qte_dispo__lt=5).order_by('qte_dispo')

    # Stats de stock
    materiels_stock_normal = Materiel.objects.filter(qte_dispo__gt=10).count()
    materiels_stock_faible = Materiel.objects.filter(qte_dispo__gte=5, qte_dispo__lte=10).count()
    materiels_stock_critique = Materiel.objects.filter(qte_dispo__lt=5).count()

    # Activité récente (simulation - en vrai il faudrait des champs de date)
    aujourd_hui = datetime.now().date()
    hier = aujourd_hui - timedelta(days=1)

    nouvelles_demandes_24h = Demande.objects.filter(date_dmd__date__gte=hier).count()
    demandes_traitees_24h = Demande.objects.filter(statuts__in=['VALIDEE', 'REFUSEE']).count()
    nouveaux_users_24h = 0  # Simulation
    demandes_semaine = Demande.objects.filter(date_dmd__date__gte=aujourd_hui - timedelta(days=7)).count()
    materiels_ajoutes_semaine = 0  # Simulation

    context = {
        'total_demandes': total_demandes,
        'total_materiels': total_materiels,
        'total_users': total_users,
        'demandes_en_attente_global': demandes_en_attente_global,
        'demandes_en_attente': demandes_en_attente,
        'demandes_validees_total': demandes_validees_total,
        'demandes_refusees_total': demandes_refusees_total,
        'materiels_critiques': materiels_critiques,
        'materiels_stock_normal': materiels_stock_normal,
        'materiels_stock_faible': materiels_stock_faible,
        'materiels_stock_critique': materiels_stock_critique,
        'nouvelles_demandes_24h': nouvelles_demandes_24h,
        'demandes_traitees_24h': demandes_traitees_24h,
        'nouveaux_users_24h': nouveaux_users_24h,
        'demandes_semaine': demandes_semaine,
        'materiels_ajoutes_semaine': materiels_ajoutes_semaine,
    }

    return render(request, 'users/dashboard_admin.html', context)
