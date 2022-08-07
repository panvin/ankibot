from disnake.ext import commands
from database.query import Query
from views.batch_management import BatchManagementView
from views.batch_select import BatchSelectView
from views.deck_management  import DeckManagementView
from views.card_management import CardManagementView
from views.deck_select import DeckSelectView
from views.modals import *
from disnake import Colour
import disnake



class SlashCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.query = Query()
    
    def get_available_batches(self, member : disnake.Member):
        #On récupère les identifiants de roles
        role_id = []
        for role in member.roles:
            role_id.append(role.id)
        return self.query.get_batches_from_roles(role_list = role_id)

    def get_available_decks(self, member : disnake.Member):
        role_id = []
        for role in member.roles:
            role_id.append(role.id)
        return self.query.get_decks_from_roles(role_list = role_id)

    def get_available_cards(self, member : disnake.Member):
        role_id = []
        for role in member.roles:
            role_id.append(role.id)
        return self.query.get_cards_from_roles(role_list = role_id)

    # Create a Batch with Modal
    @commands.slash_command(description = "Création d'une nouvelle Promotion")
    async def create_batch(self, inter: disnake.CommandInteraction):
        """Création d'une nouvelle Promotion 

        Parameters
        ---------- 
        """
        batch_modal = BatchModal(inter.id)
        await inter.response.send_modal( modal = batch_modal)
    
    
    # Create a Deck with Modal
    @commands.slash_command(description = "Création d'un nouveau Deck")
    async def create_deck(self, inter: disnake.CommandInteraction):
        """Création d'un nouveau Deck 

        Parameters
        ---------- 
        """
        batches_list = self.get_available_batches(inter.author)

        if batches_list is None or len(batches_list) == 0:
            await inter.response.send_message(" Vous n'êtes membre d'aucune promotion", ephemeral=True)
        elif len(batches_list) == 1:
            deck_modal = DeckModal(interaction_id = inter.id, batch_id = batches_list[0].id)
            await inter.response.send_modal( modal = deck_modal)
        else:
            deck_view = BatchSelectView(batches_list)
            await inter.response.send_message( "Création:" , view = deck_view, ephemeral = True)

    @commands.slash_command(description = "Création d'une nouvelle Carte question")
    async def create_card(self, inter: disnake.CommandInteraction):
        """Création d'une nouvelle Carte question

        Parameters
        ---------- 
        """
        batches_list = self.get_available_batches(inter.author)

        if batches_list is None or len(batches_list) == 0:
            await inter.response.send_message(" Vous n'êtes membre d'aucune promotion", ephemeral=True)
        elif len(batches_list) == 1:
            batch_id = batches_list[0].id
            available_deck = self.query.get_decks_list_from_batch(batch_id)
            deck_view = DeckSelectView(available_deck)
            await inter.response.send_message( "Création:" , view = deck_view, ephemeral = True)
        else:
            deck_view = BatchSelectView(batches_list)
            await inter.response.send_message( "Création:" , view = deck_view, ephemeral = True)

    def confirmation_deck_embed(self, deck_name, deck_id, deck_manager=None):
        
        if(not deck_manager):
            deck_manager="Non défini"
        
        embed = disnake.Embed(title="Création de deck", color=Colour.blue())
        deck_title="__Nom du deck:__"
        deck_value=f"{deck_name}"
        manager_title="__Responsable du dek:__"
        manager_value=f"{deck_manager}"
        help_title="__Commandes utilitaires__"
        help_value=f"__Ajout/Modification du responsable:__\n `/update_deck_manager {deck_id} <@utilisateur>/<@rôle>`\n __Gestion des decks__: `/manage_deck`"

        embed.add_field(name = deck_title,    value = deck_value,inline=False)
        embed.add_field(name = manager_title, value = manager_value,inline=False)
        embed.add_field(name = help_title,    value = help_value,inline=False)
        return embed


    @commands.slash_command(description="Gestionnaire de Promotions")
    async def manage_batches(self, inter: disnake.CommandInteraction):
        """Gestionnaire de Promotions   
        """
        batches_list = self.query.get_batches_list(inter.guild_id)
        view = BatchManagementView(batches_list)

        # Sending a message containing our view
        await inter.send("**Gestion des Promotions:** ", view=view, ephemeral=True)

    @commands.slash_command(description="Gestionnaire de Decks")
    async def manage_decks(self, inter: disnake.CommandInteraction, batch_id:int = None):
        """Menu interactif pour la gestion des Decks 

        Parameters
        ----------
        batch_id: L'identifiant unique de la promotion  
        """
        # Default behavior
        is_authorized = False

        available_batch = self.get_available_batches(inter.author)
        for batch in available_batch:
            if batch_id is not None and batch.id == int(batch_id):
                is_authorized = True

        if batch_id is None:
            deck_list = self.get_available_decks(inter.author)
            view = DeckManagementView(deck_list)
            await inter.send("**Gestion des Decks:** ", view=view, ephemeral=True)

        else:
            if is_authorized:
                deck_list = self.query.get_decks_list_from_batch(batch_id)
                if deck_list is not None and len(deck_list) != 0:
                    view = DeckManagementView(deck_list)
                    await inter.send("**Gestion des Decks:** ", view=view, ephemeral=True)
                else:
                    await inter.send("⚠️ Cette Promotion n'existe pas", ephemeral=True)
            else :
                await inter.send("⚠️ Vous n'êtes pas autorisés à accéder au contenu de cette Promotion", ephemeral=True)

    @commands.slash_command(description="Gestionnaire de Cartes")
    async def manage_cards(self, inter: disnake.CommandInteraction, deck_id : int =None):
        """Menu interactif pour la gestion des Cartes 

        Parameters
        ----------
        deck_id: L'identifiant unique du deck qui contient les Cartes.
        """
        # Default behavior
        is_authorized = False

        available_decks = self.get_available_decks(inter.author)
        for deck in available_decks:
            if deck_id is not None and deck.id == int(deck_id):
                is_authorized = True

        if deck_id is None:
            card_list = self.get_available_cards(inter.author)
            view = CardManagementView(card_list)
            await inter.send("**Gestion des Cartes:** ", view=view, ephemeral=True)

        else:
            if is_authorized:
                card_list = self.query.get_cards_list(deck_id)
                if card_list is not None and len(card_list) != 0:
                    view = CardManagementView(card_list)
                    await inter.send("**Gestion des Cartes:** ", view=view, ephemeral=True)
                else:
                    await inter.send("⚠️ Ce deck n'existe pas", ephemeral=True)
            else :
                await inter.send("⚠️ Vous n'êtes pas autorisés à accéder au contenu de ce deck", ephemeral=True)                     

    @commands.slash_command(description="Initialisation du serveur")
    async def initialize(self, inter: disnake.CommandInteraction):
        guild = inter.guild
        # On vérifie si la promo par défaut existe déjà
        if(self.query.is_default_batch_created(guild.id)):
            print(f"Promo déjà crée, suite de l'initialisation")
            await inter.send("Le bot a déjà été initialisé sur le serveur.")
        else:
            # Recherche du premier channel dans lequel on peux poster un message et on le définit comme channel par défaut
            default_channel = None
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    default_channel = channel
                break 
                        
            # Creation de la promo par défaut
            self.query.create_batch(server_id = guild.id, name = "default", manager = None, member = guild.id, channel=default_channel.id, delay = guild.id)
            print(f"Promo crée avec succès, suite de l'initialisation")
            await inter.send("La promotion a été crée avec succès, le bot est prêt")

"""
    @commands.slash_command(description="Génération de deck anki")
    async def generate_anki_deck(self, inter: disnake.CommandInteraction, ):
        my_model = genanki.Model(
        1607392319,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])

    #def generate_list_anki_deck():
"""

def setup(bot : commands.Bot):
    bot.add_cog(SlashCog(bot))