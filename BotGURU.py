import feedparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from binance.client import Client  # Importando a biblioteca da Binance

# Lista de feeds RSS que o bot irá monitorar
RSS_FEEDS = [
    'https://br.cointelegraph.com/rss',  # Exemplo: Cointelegraph
    'https://guiadobitcoin.com.br/noticias/feed/',  # Exemplo: Guia do Bitcoin
    'https://bitcoinmagazine.com/feed',  # Exemplo: Bitcoin Magazine
]

# Binance API (criar uma conta na Binance e gerar as chaves de API)
BINANCE_API_KEY = 'SUA_API_KEY_AQUI'
BINANCE_API_SECRET = 'SUA_API_SECRET_AQUI'
binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)  # Inicializando o cliente da Binance

# Função para ler o feed RSS
def get_rss_feed(url):
    feed = feedparser.parse(url)
    entries = feed.entries[:5]  # Vamos pegar os 5 primeiros itens do feed
    return entries

# Função para obter o valor atual do Bitcoin na Binance
def get_bitcoin_price_binance():
    ticker = binance_client.get_symbol_ticker(symbol="BTCUSDT")  # Obtendo o preço de BTC/USDT
    return ticker['price']  # Retorna o preço de Bitcoin em USD

# Função para obter o valor atual do Bitcoin (alternativo - usando Coingecko)
def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data['bitcoin']['usd']  # Retorna o valor do Bitcoin em USD

# Função para enviar as últimas notícias de RSS para os usuários
async def send_rss_updates(update: Update, context: CallbackContext):
    message = "Últimas atualizações dos feeds RSS:\n\n"
    
    for rss_url in RSS_FEEDS:
        feed_entries = get_rss_feed(rss_url)
        
        if feed_entries:
            message += f"Feed: {rss_url}\n"
            for entry in feed_entries:
                message += f"• {entry.title}\n{entry.link}\n\n"
    
    # Enviar a mensagem com as últimas notícias
    await update.callback_query.message.edit_text(message)

# Função do comando /start
async def start(update: Update, context: CallbackContext):
    # Adiciona o usuário à lista de usuários para enviar as atualizações futuras
    user_id = update.message.from_user.id
    context.chat_data.setdefault("user_ids", set()).add(user_id)
    
    # Obter o valor atual do Bitcoin na Binance
    bitcoin_price_binance = get_bitcoin_price_binance()
    
    # Criar os botões com os links
    youtube_button = InlineKeyboardButton(text="Visite nosso Canal no YouTube", url="https://www.youtube.com/@OGrandeGuru")
    tiktok_button = InlineKeyboardButton(text="Siga-nos no TikTok", url="https://www.tiktok.com/@empresa")
    website_button = InlineKeyboardButton(text="Visite nosso Website", url="https://www.suaempresa.com.br")
    rss_button = InlineKeyboardButton(text="Últimas Notícias sobre Criptomoedas", callback_data='rss')
    whatsapp_button = InlineKeyboardButton(text="Fale com o Grande Guru", url="https://wa.me/351927581400")  # Adicionando botão para o WhatsApp

    # Agrupando os botões em uma linha ou em múltiplas linhas
    keyboard = InlineKeyboardMarkup([
        [youtube_button],
        [tiktok_button],
        [website_button],
        [rss_button],
        [whatsapp_button]  # Botão do WhatsApp
    ])
    
    # Enviar a mensagem com o valor do Bitcoin e os botões
    await update.message.reply_text(
        f'Olá! Fique por dentro das principais notícias do mundo da Criptomoeda.\n\n'
        f'O valor atual do Bitcoin na Binance é: ${bitcoin_price_binance}\n\n'
        'Clique nos botões abaixo para nos seguir e ficar conectado!',
        reply_markup=keyboard
    )

# Função para configurar o agendamento
def schedule_rss_updates(application, job_queue):
    scheduler = BackgroundScheduler()

    # Agendar o envio de RSS
    scheduler.add_job(
        send_rss_updates,
        'interval',
        minutes=1,  # Envia o RSS a cada 1 minuto
        args=[application, job_queue],
        id='send_rss_updates_job',
        replace_existing=True
    )
    
    scheduler.start()

def main():
    # Substitua pelo seu token
    token = '8083112203:AAGuXWOaMqHl3ixluP3Xh5uMeVBJ9LVS84o'

    # Criação do Application
    application = Application.builder().token(token).build()

    # Adiciona o handler do comando /start
    application.add_handler(CommandHandler('start', start))

    # Adiciona o handler para qualquer mensagem que não seja um comando específico
    # Ele irá chamar a função start() sempre que uma mensagem for recebida
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    # Adiciona o handler para o botão de "Últimas Notícias"
    application.add_handler(CallbackQueryHandler(send_rss_updates, pattern='rss'))

    # Inicia o agendamento de atualizações RSS
    schedule_rss_updates(application, application.job_queue)

    # Inicia o bot
    application.run_polling()

if __name__ == '__main__':
    main()
