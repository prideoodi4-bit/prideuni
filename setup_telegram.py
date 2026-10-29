"""Optional manual Telegram reconfiguration; deployment also configures automatically."""
import asyncio
from app import configure_telegram,PUBLIC,SECRET,TOKEN

async def main():
 if not TOKEN or not PUBLIC.startswith('https://') or len(SECRET)<32:
  raise SystemExit('Set BOT_TOKEN, HTTPS PUBLIC_URL/RENDER_EXTERNAL_URL and WEBHOOK_SECRET first.')
 await configure_telegram()
 print('Webhook, menu button and commands configured successfully.')

if __name__=='__main__':
 asyncio.run(main())
