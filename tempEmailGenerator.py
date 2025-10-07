import html
import json
import os
import requests
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import re
import html2text

API_BASE = "https://api.mail.tm"


class TempEmailBot:
    def __init__(self):
        self.user_data = {}
        self.data_file = "user_data.json"  # Initialize data_file
        self.load_user_data()

    def load_user_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.user_data = json.load(f)
                    self.user_data = {int(k): v for k, v in self.user_data.items()}
        except Exception as e:
            print(f"Erreur chargement données JSON: {e}")
            self.user_data = {}

    def save_user_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde données JSON: {e}")

    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_domains(self):
        try:
            response = requests.get(f"{API_BASE}/domains", timeout=10)
            if response.status_code == 200:
                domains = response.json()
                if domains and 'hydra:member' in domains:
                    return [d['domain'] for d in domains['hydra:member']]
        except Exception as e:
            print(f"Erreur récupération domaines: {e}")
        return []

    def create_account(self, user_id):
        try:
            domains = self.get_domains()
            if not domains:
                print("Aucun domaine disponible")
                return None

            domain = random.choice(domains)
            username = self.generate_random_string(8)
            email = f"{username}@{domain}"
            password = self.generate_random_string(12)

            data = {
                "address": email,
                "password": password
            }

            response = requests.post(
                f"{API_BASE}/accounts",
                json=data,
                timeout=10
            )

            print(f"Create account status: {response.status_code}")

            if response.status_code == 201:
                token = self.login(email, password)
                if token:
                    account = {
                        "email": email,
                        "password": password,
                        "token": token
                    }
                    self.user_data[user_id] = account  # Use provided user_id
                    self.save_user_data()
                    return account
        except Exception as e:
            print(f"Erreur création compte: {e}")
        return None

    def login(self, email, password):
        try:
            data = {
                "address": email,
                "password": password
            }
            response = requests.post(
                f"{API_BASE}/token",
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('token')
        except Exception as e:
            print(f"Erreur login: {e}")
        return None

    def get_messages(self, token):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{API_BASE}/messages",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('hydra:member', [])
        except Exception as e:
            print(f"Erreur récupération messages: {e}")
        return []

    def get_message(self, token, message_id):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{API_BASE}/messages/{message_id}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erreur lecture message: {e}")
        return None

    async def nouveau(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        msg = await update.message.reply_text("⏳ Création d'une nouvelle adresse email sécurisée...")

        account = self.create_account(user_id)

        if account:
            keyboard = [
                [InlineKeyboardButton("📬 Voir inbox", callback_data='check_inbox')],
                [InlineKeyboardButton("🔄 Nouvelle adresse", callback_data='new_email')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                f"✅ *Adresse créée avec succès!*\n\n"
                f"📧 `{account['email']}`\n\n"
                f"⏱️ Cette adresse est valide pendant 24-48h\n"
                f"🔒 Vos emails sont chiffrés et sécurisés\n\n"
                f"Utilisez /inbox pour vérifier vos messages."
            )

            await msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await msg.edit_text(
                "❌ Erreur lors de la création. Le service est peut-être temporairement indisponible.\n\n"
                "Réessayez dans quelques instants."
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id

        if query.data == 'check_inbox':
            if user_id not in self.user_data:
                await query.edit_message_text(
                    "❌ Aucune adresse email active.\n"
                    "Utilisez /nouveau"
                )
                return

            data = self.user_data[user_id]
            messages = self.get_messages(data['token'])

            if not messages:
                await query.edit_message_text(
                    f"📭 Aucun email reçu pour:\n{data['email']}"
                )
            else:
                await query.edit_message_text(
                    f"📬 {len(messages)} email(s) reçu(s)!\n\n"
                    "Utilisez /inbox pour les voir."
                )

        elif query.data == 'new_email':
            await query.edit_message_text("⏳ Création en cours...")

            account = self.create_account(user_id)
            if account:
                keyboard = [
                    [InlineKeyboardButton("📬 Voir inbox", callback_data='check_inbox')],
                    [InlineKeyboardButton("🔄 Nouvelle adresse", callback_data='new_email')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    f"✅ *Nouvelle adresse créée!*\n\n"
                    f"📧 `{account['email']}`",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text(
                    "❌ Erreur de création. Réessayez."
                )


bot_instance = TempEmailBot()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start"""
    welcome_text = (
        "🔒 *Bot Email Temporaire*\n\n"
        "Bienvenue ! Je crée des adresses email temporaires sécurisées.\n\n"
        "*Commandes disponibles:*\n"
        "/nouveau - Créer une nouvelle adresse email\n"
        "/inbox - Voir les emails reçus\n"
        "/email - Afficher votre adresse actuelle\n"
        "/aide - Afficher l'aide\n\n"
        "⏱️ Les emails sont conservés pendant 24-48 heures"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les emails reçus"""
    user_id = update.effective_user.id

    if user_id not in bot_instance.user_data:
        await update.message.reply_text(
            "❌ Aucune adresse email active.\n"
            "Utilisez /nouveau pour en créer une."
        )
        return

    data = bot_instance.user_data[user_id]

    msg = await update.message.reply_text("🔍 Vérification de votre boîte de réception...")

    messages = bot_instance.get_messages(data['token'])

    if not messages:
        await msg.edit_text(
            f"📭 *Aucun email reçu*\n\n"
            f"📧 {data['email']}\n\n"
            "Vérifiez à nouveau dans quelques instants."
        )
        return

    response = f"📬 *Inbox: {data['email']}*\n\n"
    response += f"*{len(messages)} message(s) reçu(s):*\n\n"

    for i, msg_data in enumerate(messages[:10], 1):
        sender = msg_data.get('from', {}).get('address', 'Inconnu')
        subject = msg_data.get('subject', 'Sans objet')
        date = msg_data.get('createdAt', '')[:10]
        msg_id = msg_data.get('id', '')

        response += f"{i}. 📧 *De:* {sender}\n"
        response += f"   *Objet:* {subject}\n"
        response += f"   *Date:* {date}\n"
        response += f"   /read\\_{msg_id}\n\n"

    await msg.edit_text(response, parse_mode='Markdown')


async def email_actuel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche l'adresse email actuelle"""
    user_id = update.effective_user.id

    if user_id not in bot_instance.user_data:
        await update.message.reply_text(
            "❌ Aucune adresse email active.\n"
            "Utilisez /nouveau pour en créer une."
        )
        return

    email = bot_instance.user_data[user_id]['email']

    keyboard = [
        [InlineKeyboardButton("📬 Voir inbox", callback_data='check_inbox')],
        [InlineKeyboardButton("🔄 Nouvelle adresse", callback_data='new_email')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📧 *Votre adresse actuelle:*\n\n`{email}`\n\n"
        f"⏱️ Valide pendant 24-48 heures",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def read_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lit un message spécifique"""
    user_id = update.effective_user.id

    if user_id not in bot_instance.user_data:
        await update.message.reply_text("❌ Aucune adresse email active.")
        return

    text = update.message.text
    if not text.startswith('/read_'):
        return

    msg_id = text.replace('/read_', '')
    data = bot_instance.user_data[user_id]

    msg = await update.message.reply_text("📖 Chargement du message...")

    message = bot_instance.get_message(data['token'], msg_id)

    if message:
        sender = message.get('from', {}).get('address', 'Inconnu')
        subject = message.get('subject', 'Sans objet')
        text_content = message.get('text', 'Pas de contenu texte')
        html_content = message.get('html', [''])[0] if message.get('html') else ''

        # Convertir HTML en texte brut avec liens inline
        h = html2text.HTML2Text()
        h.body_width = 0  # Éviter le retour à la ligne automatique
        h.inline_links = True  # Garder les liens dans le texte
        h.ignore_images = True  # Ignorer les images pour réduire la taille
        content = h.handle(html_content) if html_content else text_content

        # Limiter la taille du contenu pour Telegram (4096 caractères)
        max_content_length = 3800  # Réserve plus d'espace pour l'en-tête
        if len(content) > max_content_length:
            content = content[:max_content_length] + "...\n\n[Message tronqué]"

        # Construire la réponse en HTML (plus simple et plus fiable)
        response = (
            f"📧 <b>Message</b>\n\n"
            f"<b>De:</b> {html.escape(sender)}\n"
            f"<b>Objet:</b> {html.escape(subject)}\n\n"
            f"{html.escape(content)}"
        )

        try:
            await msg.edit_text(response, parse_mode='HTML')
        except Exception as e:
            print(f"Erreur HTML: {e}")
            # Fallback to plain text if HTML fails
            response = (
                f"📧 Message\n\n"
                f"De: {sender}\n"
                f"Objet: {subject}\n\n"
                f"{content}"
            )
            await msg.edit_text(response, parse_mode=None)
    else:
        await msg.edit_text("❌ Impossible de charger le message.")


async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche l'aide"""
    help_text = (
        "📚 *Guide d'utilisation*\n\n"
        "*Commandes:*\n"
        "/nouveau - Créer une adresse email temporaire\n"
        "/inbox - Vérifier les emails reçus\n"
        "/email - Afficher votre adresse actuelle\n"
        "/aide - Afficher ce message\n\n"
        "*Informations importantes:*\n"
        "⏱️ Les emails sont conservés 24-48 heures\n"
        "🔒 Connexion sécurisée et chiffrée\n"
        "♻️ Parfait pour les inscriptions test\n"
        "⚠️ Ne pas utiliser pour des infos sensibles\n\n"
        "*Pour lire un email:*\n"
        "1. Utilisez /inbox pour voir la liste\n"
        "2. Cliquez sur /read_ID du message"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


def main():
    """Fonction principale"""
    TOKEN = "your token"  # ⚠️ Remplacez par un nouveau token généré via @BotFather

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nouveau", bot_instance.nouveau))
    app.add_handler(CommandHandler("inbox", inbox))
    app.add_handler(CommandHandler("email", email_actuel))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(MessageHandler(filters.Regex(r'^/read_'), read_message))
    app.add_handler(CallbackQueryHandler(bot_instance.button_callback))

    print("🤖 Bot démarré avec Mail.tm API!")
    print("📧 Service d'email temporaire opérationnel")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()