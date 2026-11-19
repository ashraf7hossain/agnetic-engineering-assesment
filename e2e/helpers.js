/**
 * @param {import('@playwright/test').Page} page
 * @param {{ username: string, email: string, password: string }} user
 */
async function register(page, user) {
  await page.goto("/accounts/register/");
  await page.locator("#id_username").fill(user.username);
  await page.locator("#id_email").fill(user.email);
  await page.locator("#id_password1").fill(user.password);
  await page.locator("#id_password2").fill(user.password);
  await page.locator("main form button[type=submit]").click();
  await page.waitForURL("**/dashboard/**");
}

/**
 * @param {import('@playwright/test').Page} page
 * @param {{ username: string, password: string }} user
 */
async function login(page, user) {
  await page.goto("/accounts/login/");
  await page.locator("#id_username").fill(user.username);
  await page.locator("#id_password").fill(user.password);
  await page.locator("main form button[type=submit]").click();
  await page.waitForURL("**/dashboard/**");
}

/**
 * @param {import('@playwright/test').Page} page
 * @param {{ name: string, slug: string, headerTitle: string, message: string }} space
 */
async function createSpace(page, space) {
  await page.goto("/spaces/new/");
  await page.locator("#id_name").fill(space.name);
  await page.locator("#id_slug").fill(space.slug);
  await page.locator("#id_header_title").fill(space.headerTitle);
  await page.locator("#id_message").fill(space.message);
  if (!(await page.locator("#id_collect_ratings").isChecked())) {
    await page.locator("#id_collect_ratings").check();
  }
  await page.locator("#id_theme").selectOption("light");
  await page.locator("main form button[type=submit]").click();
  await page.waitForURL(`**/spaces/${space.slug}/`);
}

/**
 * Unique suffix for parallel-safe usernames/slugs.
 */
function uid() {
  return `${Date.now()}${Math.floor(Math.random() * 1000)}`;
}

module.exports = { register, login, createSpace, uid };
