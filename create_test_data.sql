-- Script SQL pour créer les données de test
-- Exécuter ce script dans PostgreSQL

-- 1. Créer les types d'utilisateurs
INSERT INTO mywitti_user_type (id, type_name, description, permissions, is_active, created_at, updated_at) VALUES
(1, 'superadmin', 'Super administrateur', '{"all": true}', true, NOW(), NOW()),
(2, 'admin', 'Administrateur', '{"logs":{"read":true},"stats":{"read":true},"clients":{"read":true, "update":true},"passwords":{"reset":true}}', true, NOW(), NOW()),
(3, 'manager', 'Manager', '{"logs":{"read":true},"stats":{"read":true},"clients":{"read":true}}', true, NOW(), NOW()),
(4, 'client', 'Client standard', '{"own_data":{"read":true, "update":true}}', true, NOW(), NOW());

-- 2. Créer les catégories
INSERT INTO mywitti_category (id, category_name, slug, description, categ_points, recompense_point, created_at, level, min_jetons, nb_jours) VALUES
(1, 'Eco Premium', 'ECO', 'Catégorie Eco Premium', 10, 99, NOW(), 1, 1, 90),
(2, 'Executive', 'EXE', 'Catégorie Executive', 50, 999, NOW(), 2, 100, 90),
(3, 'Executive +', 'EXEC', 'Catégorie Executive', 100, 3000, NOW(), 3, 1000, 90),
(4, 'First Class', 'FIRST', 'Catégorie First Class', 200, 60000, NOW(), 4, 3000, 90);

-- 3. Créer l'utilisateur superadmin
-- Mot de passe hashé pour "123456"
INSERT INTO mywitti_users (id, user_id, password, first_name, last_name, user_type, date_joined, last_login, is_active, is_staff, must_change_password, user_type_id, email) VALUES
(1, 'superadmin', 'scrypt:32768:8:1$yrKXPo7EYhGuBGHq$0e1fb5ef9b6310842073f9557c63639f388e541b9c9be38a255064dc0789aaa8119572c2d9abbdb9e549b2f88a413b47352c3f5898b91167ba7b7dda912c36ed', 'Super', 'Admin', 'superadmin', NOW(), NOW(), true, true, false, 1, 'superadmin@gmail.com');

-- 4. Créer l'utilisateur client de test
INSERT INTO mywitti_users (id, user_id, password, first_name, last_name, user_type, date_joined, last_login, is_active, is_staff, must_change_password, user_type_id, email) VALUES
(2, 'user_test', 'scrypt:32768:8:1$yrKXPo7EYhGuBGHq$0e1fb5ef9b6310842073f9557c63639f388e541b9c9be38a255064dc0789aaa8119572c2d9abbdb9e549b2f88a413b47352c3f5898b91167ba7b7dda912c36ed', 'User', 'Test', 'client', NOW(), NOW(), true, false, false, 4, 'user_test@gmail.com');

-- 5. Créer le client superadmin
INSERT INTO mywitti_client (id, customer_code, short_name, first_name, gender, birth_date, phone_number, street, jetons, date_ouverture, nombre_jours, category_id, user_id) VALUES
(1, 'superadmin', 'Admin', 'Super', 'M', '1985-01-01', '+2250710922213', '123 Avenue Admin, Abidjan', 10000, '2025-01-01', 365, 4, 1);

-- 6. Créer le client associé à user_test
INSERT INTO mywitti_client (id, customer_code, short_name, first_name, gender, birth_date, phone_number, street, jetons, date_ouverture, nombre_jours, category_id, user_id) VALUES
(2, 'user_test', 'Test', 'User', 'M', '1990-01-01', '+22501234567', '123 Rue Test, Abidjan', 500, '2025-01-01', 30, 2, 2);

-- 7. Créer quelques lots de test
INSERT INTO mywitti_lots (id, libelle, slug, recompense_image, jetons, stock, created_at, category_id) VALUES
(1, 'Carte cadeau 5000 FCFA', 'carte-cadeau-5000', '/static/uploads/gift-card.jpg', 50, 100, NOW(), 1),
(2, 'Carte cadeau 10000 FCFA', 'carte-cadeau-10000', '/static/uploads/gift-card.jpg', 100, 50, NOW(), 2),
(3, 'Smartphone Samsung', 'smartphone-samsung', '/static/uploads/smartphone.jpg', 1500, 10, NOW(), 3),
(4, 'Voyage à Paris', 'voyage-paris', '/static/uploads/paris.jpg', 5000, 2, NOW(), 4);

-- 8. Créer quelques transactions de test pour user_test
INSERT INTO mywitti_jetons_transactions (id, client_id, lot_id, montant, motif, date_transaction) VALUES
(1, 2, 1, 50, 'Achat carte cadeau', NOW() - INTERVAL '5 days'),
(2, 2, 2, 100, 'Achat carte cadeau', NOW() - INTERVAL '3 days'),
(3, 2, NULL, 200, 'Bonus fidélité', NOW() - INTERVAL '1 day');

-- 9. Créer quelques transactions de test pour superadmin
INSERT INTO mywitti_jetons_transactions (id, client_id, lot_id, montant, motif, date_transaction) VALUES
(4, 1, 4, 5000, 'Achat voyage Paris', NOW() - INTERVAL '10 days'),
(5, 1, 3, 1500, 'Achat smartphone', NOW() - INTERVAL '7 days'),
(6, 1, NULL, 5000, 'Bonus administrateur', NOW() - INTERVAL '2 days');

-- 10. Créer quelques notifications de test
INSERT INTO mywitti_notification (id, user_id, message, created_at, is_read) VALUES
(1, 2, 'Bienvenue sur la plateforme MyWitti !', NOW() - INTERVAL '7 days', false),
(2, 2, 'Votre commande #123 a été validée', NOW() - INTERVAL '2 days', false),
(3, 1, 'Nouveau client inscrit : user_test', NOW() - INTERVAL '1 day', false),
(4, 1, 'Système de jetons mis à jour', NOW() - INTERVAL '5 days', false),
(5, 1, 'Nouvelle fonctionnalité disponible', NOW() - INTERVAL '3 days', false);

-- 11. Créer quelques FAQs de test
INSERT INTO faqs (id, question, answer) VALUES
(1, 'Comment fonctionne le système de jetons ?', 'Les jetons sont des points que vous gagnez en utilisant nos services. Vous pouvez les échanger contre des récompenses.'),
(2, 'Comment passer une commande ?', 'Allez dans la section "Lots" et sélectionnez l''article de votre choix. Ajoutez-le au panier et validez votre commande.'),
(3, 'Comment contacter le support ?', 'Vous pouvez nous contacter via l''onglet "Support" ou par téléphone au +2250710922213.');

-- 12. Créer un sondage de test
INSERT INTO surveys (id, title, description, created_at, updated_at, is_active) VALUES
(1, 'Satisfaction générale', 'Comment évaluez-vous votre expérience sur notre plateforme ?', NOW(), NOW(), true);

-- 13. Créer les options du sondage
INSERT INTO survey_options (id, survey_id, option_text, option_value) VALUES
(1, 1, 'Très mal', 1),
(2, 1, 'Mal', 2),
(3, 1, 'Moyen', 3),
(4, 1, 'Bien', 4),
(5, 1, 'Très bien', 5);

-- Afficher les données créées
SELECT 'Utilisateurs créés :' as info;
SELECT id, user_id, email, user_type, is_active FROM mywitti_users;

SELECT 'Clients créés :' as info;
SELECT id, customer_code, first_name, jetons, category_id FROM mywitti_client;

SELECT 'Catégories créées :' as info;
SELECT id, category_name, min_jetons FROM mywitti_category ORDER BY level; 