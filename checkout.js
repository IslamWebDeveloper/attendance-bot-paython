import { chromium } from 'playwright';

const ERP_URL = process.env.ERP_URL || 'https://techsup-erp.com/my/attendance';
const EMAIL = process.env.ERP_EMAIL || 'Islam@techsupbusiness.com';
const PASSWORD = process.env.ERP_PASSWORD || 'Ii@123123';

async function main() {
  console.log('🚀 Starting Odoo Auto Checkout Bot (Node Playwright)...');
  
  if (!EMAIL || !PASSWORD) {
    console.error('❌ Missing ERP_EMAIL or ERP_PASSWORD environment variables.');
    process.exit(1);
  }

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });

  const page = await context.newPage();

  // Accept JS confirmation popup automatically
  page.on('dialog', async dialog => {
    console.log(`💬 Dialog box: "${dialog.message()}". Accepting...`);
    await dialog.accept();
  });

  try {
    const loginUrl = `${ERP_URL}/web/login?redirect=/my/attendance`;
    console.log(`🔗 Navigating to: ${loginUrl}`);
    await page.goto(loginUrl, { waitUntil: 'networkidle' });

    console.log('🔑 Entering credentials...');
    await page.fill('input[name="login"], #login', EMAIL);
    await page.fill('input[name="password"], #password', PASSWORD);

    console.log('👆 Clicking login button...');
    await page.click('button[type="submit"]');

    await page.waitForURL('**/my/attendance*', { timeout: 20000 });
    console.log('✅ Navigated to Attendance Portal.');

    const checkoutBtn = page.locator('form[action*="/my/attendance/checkout"] button[type="submit"]');
    const btnCount = await checkoutBtn.count();

    if (btnCount > 0) {
      console.log('🛑 Clicking "Check out" button...');
      await checkoutBtn.first().click();
      await page.waitForLoadState('networkidle');
      console.log('🎉 Successfully checked out!');
    } else {
      console.log('ℹ️ Check out button not found. User may already be checked out.');
    }
  } catch (error) {
    console.error('❌ Error during checkout:', error);
    process.exit(1);
  } finally {
    await browser.close();
    console.log('🔒 Browser closed. Done.');
  }
}

main();
