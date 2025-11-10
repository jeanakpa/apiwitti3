from extensions import db
from Models.mywitti_faq import MyWittiFAQ

def seed_faqs():
    faqs = [
        # Généralités sur le programme
        MyWittiFAQ(question="Qu'est-ce que le programme de récompense pour épargnants ?", 
            answer="C'est un programme qui récompense nos clients fidèles pour leur effort d'épargne. Plus vous épargnez régulièrement, plus vous cumulez des points convertibles en récompenses."),
        
        MyWittiFAQ(question="Pourquoi avez-vous mis en place cette application ?", 
            answer="Nous voulons encourager la culture de l'épargne et récompenser nos clients les plus engagés. L'application permet de suivre vos points et de bénéficier de cadeaux ou avantages."),
        
        MyWittiFAQ(question="Qui peut bénéficier de ce programme ?", 
            answer="Tous nos clients titulaires d'un compte d'épargne actif sont automatiquement éligibles au programme."),
        
        MyWittiFAQ(question="L'adhésion au programme est-elle payante ?", 
            answer="Non. L'adhésion au programme est gratuite pour tous nos clients épargnants."),
        
        MyWittiFAQ(question="Comment puis-je m'inscrire au programme ?", 
            answer="Aucune inscription n'est requise. Une fois que vous ouvrez un compte d'épargne chez nous, vous êtes automatiquement intégré au programme."),
        
        MyWittiFAQ(question="Est-ce que le programme est disponible pour les comptes entreprises ?", 
            answer="Pour l'instant, ce programme est réservé aux particuliers, mais une extension aux comptes entreprises est en étude."),
        
        # Fonctionnement des récompenses
        MyWittiFAQ(question="Comment accumule-t-on des points ou des récompenses ?", 
            answer="Vous gagnez des points en épargnant régulièrement, en atteignant certains seuils, ou en respectant des objectifs définis dans l'application."),
        
        MyWittiFAQ(question="Quelles sont les actions qui permettent de gagner des points ?", 
            answer="Par exemple : - Dépôt mensuel minimum régulier - Augmentation du solde d'épargne - Maintien d'un solde sans retrait pendant une période donnée"),
        
        MyWittiFAQ(question="Comment sont calculées les récompenses ?", 
            answer="Les récompenses sont basées sur un système de points liés au montant et à la durée de votre épargne. Plus vous épargnez, plus vous êtes récompensé."),
        
        # Utilisation des récompenses
        MyWittiFAQ(question="Quelles sont les récompenses proposées ?", 
            answer="Les récompenses varient : - Bons d'achat - Paniers cadeaux - Séance au spa - Tickets Brunch"),
        
        MyWittiFAQ(question="Comment puis-je consulter mes points ?", 
            answer="Vous pouvez consulter vos points à tout moment via l'application, dans les rubriques 'Dashboard', 'Profil' et 'Mes récompenses'."),
        
        MyWittiFAQ(question="Comment puis-je échanger mes points contre des récompenses ?", 
            answer="Dans l'application, une boutique de récompenses est disponible. Il vous suffit de choisir une récompense et de valider avec vos points."),
        
        MyWittiFAQ(question="Puis-je offrir mes points à un autre client ?", 
            answer="Non, les points sont nominatifs et non transférables."),
        
        # Sécurité et confidentialité
        MyWittiFAQ(question="Mes informations personnelles sont-elles sécurisées dans l'application ?", 
            answer="Oui, nous utilisons les standards de sécurité bancaire les plus élevés pour protéger vos données."),
        
        MyWittiFAQ(question="Que faire si je soupçonne une utilisation frauduleuse de mon compte ?", 
            answer="Veuillez contacter immédiatement notre service client ou bloquer temporairement l'accès via l'application."),
        
        MyWittiFAQ(question="Comment réinitialiser mon mot de passe ?", 
            answer="Sur l'écran de connexion, cliquez sur 'Mot de passe oublié' et suivez les instructions pour réinitialiser votre accès."),
        
        # Assistance et support
        MyWittiFAQ(question="Qui contacter en cas de problème technique avec l'application ?", 
            answer="Vous pouvez contacter notre support via le bouton 'Assistance' dans l'application ou appeler notre service client au 25 22 00 98 05."),
        
        MyWittiFAQ(question="L'application est-elle disponible sur Android et iOS ?", 
            answer="Oui, l'application est disponible sur le Play Store et l'App Store."),
        
        MyWittiFAQ(question="Que faire si mes points ne s'affichent pas correctement ?", 
            answer="Attendez 48h. Si le problème persiste, contactez notre support client avec une capture d'écran du problème."),
        
        MyWittiFAQ(question="Y a-t-il un centre d'aide ou une assistance téléphonique ?", 
            answer="Oui, notre service client est disponible du lundi au vendredi de 9h à 17h."),
        
        # Conditions spécifiques
        MyWittiFAQ(question="Puis-je participer au programme avec plusieurs comptes ?", 
            answer="Le programme est lié à votre profil client. Les points de tous vos comptes épargnes actifs sont cumulés ensemble."),
        
        MyWittiFAQ(question="Y a-t-il des conditions particulières pour bénéficier de certaines récompenses ?", 
            answer="Oui, certaines récompenses sont réservées aux clients ayant atteint un niveau spécifique ou respecté une certaine régularité."),
        
        MyWittiFAQ(question="Le programme peut-il être modifié ou annulé par l'institution ?", 
            answer="Oui, l'institution se réserve le droit de modifier ou d'interrompre le programme, avec une communication préalable aux clients."),
        
        MyWittiFAQ(question="Où puis-je consulter les conditions générales du programme de récompense ?", 
            answer="Les conditions générales sont disponibles dans l'application, rubrique 'Informations légales'."),
        
        # FAQs supplémentaires pour la gestion des commandes
        MyWittiFAQ(question="Comment puis-je consulter mon solde de jetons ?", 
            answer="Vous pouvez consulter votre solde de jetons sur votre tableau de bord ou dans la section Profil de l'application."),
        
        MyWittiFAQ(question="Que faire si ma commande est annulée ?", 
            answer="Si votre commande est annulée, vous recevrez une notification expliquant la raison. Contactez l'agence RGK pour plus d'informations."),
        
        MyWittiFAQ(question="Comment passer à la catégorie suivante ?", 
            answer="Pour passer à la catégorie suivante, vous devez accumuler plus de jetons. Consultez votre tableau de bord pour voir combien de jetons il vous manque."),
        
        MyWittiFAQ(question="Où puis-je récupérer ma commande validée ?", 
            answer="Une fois votre commande validée, vous pouvez la récupérer à l'agence RGK. Apportez votre identifiant client."),
        
        MyWittiFAQ(question="Comment ajouter un article à mes favoris ?", 
            answer="Pour ajouter un article à vos favoris, accédez à la liste des récompenses et cliquez sur l'icône de cœur à côté de l'article.")
    ]
    
    try:
        db.session.bulk_save_objects(faqs)
        db.session.commit()
        print(f"✅ {len(faqs)} FAQs ont été insérées avec succès dans la base de données.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur lors de l'insertion des FAQs : {str(e)}")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_faqs()