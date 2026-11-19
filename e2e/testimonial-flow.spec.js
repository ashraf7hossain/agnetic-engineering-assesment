const { test, expect } = require("@playwright/test");
const { register, createSpace, uid } = require("./helpers");

test.describe("Testimonial end-to-end", () => {
  test("create space → submit → approve → wall", async ({ page, context }) => {
    const id = uid();
    const user = {
      username: `owner_${id}`,
      email: `owner_${id}@example.com`,
      password: "DemoPass123!",
    };
    const space = {
      name: "Acme E2E",
      slug: `acme-${id}`,
      headerTitle: "Share your experience with Acme",
      message: "Tell us how Acme helped you.",
    };

    await register(page, user);
    await createSpace(page, space);
    await expect(page.getByRole("heading", { name: space.name })).toBeVisible();
    await expect(page.getByText("Pending")).toBeVisible();

    // Public collect in a clean context (anonymous)
    const guest = await context.browser().newPage();
    await guest.goto(`/s/${space.slug}/`);
    await expect(guest.getByRole("heading", { name: space.headerTitle })).toBeVisible();
    await guest.locator("#id_name").fill("Jordan Lee");
    await guest.locator("#id_email").fill("jordan@example.com");
    await guest.locator("#id_body").fill("Acme cut our deploy time in half.");
    await guest.locator("input[name=rating][value='5']").check();
    await guest.locator("#id_consent").check();
    await guest.locator("main form button[type=submit]").click();
    await expect(guest.getByText("Thank you!")).toBeVisible();
    await guest.close();

    // Wall empty until approved
    await page.goto(`/s/${space.slug}/wall/`);
    await expect(page.getByText("No approved testimonials yet.")).toBeVisible();

    // Inbox approve via HTMX
    await page.goto(`/spaces/${space.slug}/inbox/`);
    await expect(page.getByText("Jordan Lee")).toBeVisible();
    await page.locator("button:has-text('Approve')").click();
    await expect(page.getByText(/Approved ·/)).toBeVisible();

    // Wall shows approved only
    await page.goto(`/s/${space.slug}/wall/`);
    await expect(page.getByRole("heading", { name: "Wall of Love" })).toBeVisible();
    await expect(page.getByText("Acme cut our deploy time in half.")).toBeVisible();
    await expect(page.getByText("— Jordan Lee")).toBeVisible();
  });

  test("reject keeps testimonial off the wall", async ({ page }) => {
    const id = uid();
    const user = {
      username: `rej_${id}`,
      email: `rej_${id}@example.com`,
      password: "DemoPass123!",
    };
    const space = {
      name: "Reject Co",
      slug: `reject-${id}`,
      headerTitle: "Leave feedback",
      message: "We read every submission.",
    };

    await register(page, user);
    await createSpace(page, space);

    await page.goto(`/s/${space.slug}/`);
    await page.locator("#id_name").fill("Sam");
    await page.locator("#id_email").fill("sam@example.com");
    await page.locator("#id_body").fill("Not for the wall.");
    await page.locator("input[name=rating][value='2']").check();
    await page.locator("#id_consent").check();
    await page.locator("main form button[type=submit]").click();
    await expect(page.getByText("Thank you!")).toBeVisible();

    // Still authenticated as owner from register/create
    await page.goto(`/spaces/${space.slug}/inbox/`);
    await page.locator("button:has-text('Reject')").click();
    await expect(page.getByText(/Rejected ·/)).toBeVisible();

    await page.goto(`/s/${space.slug}/wall/`);
    await expect(page.getByText("Not for the wall.")).toHaveCount(0);
    await expect(page.getByText("No approved testimonials yet.")).toBeVisible();
  });

  test("non-owner cannot open inbox", async ({ page, context }) => {
    const id = uid();
    const owner = {
      username: `own_${id}`,
      email: `own_${id}@example.com`,
      password: "DemoPass123!",
    };
    const other = {
      username: `oth_${id}`,
      email: `oth_${id}@example.com`,
      password: "DemoPass123!",
    };
    const space = {
      name: "Private Space",
      slug: `priv-${id}`,
      headerTitle: "Private",
      message: "Owner only moderation.",
    };

    await register(page, owner);
    await createSpace(page, space);
    await page.locator("header form button[type=submit]").click();

    const otherPage = await context.browser().newPage();
    await register(otherPage, other);
    const res = await otherPage.goto(`/spaces/${space.slug}/inbox/`);
    expect(res.status()).toBe(403);
    await otherPage.close();
  });
});
