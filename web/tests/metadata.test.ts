// REQ-009, AC-004: the browser tab shows the product name, never a framework default.
import { describe, expect, it } from "vitest";
import { metadata } from "@/app/layout";
import { SITE_NAME } from "@/lib/site";

describe("the tab title", () => {
  it("is the product name", () => {
    expect(SITE_NAME).toBe("Market Intel");
    expect(metadata.title).toBe(SITE_NAME);
  });

  it("is not a framework default and holds only Latin letters", () => {
    expect(String(metadata.title)).not.toMatch(/create next app/i);
    expect(String(metadata.description)).not.toMatch(/create next app/i);
    expect(String(metadata.title)).not.toMatch(/[Ⴀ-ჿᲐ-Ჿ]/);
  });
});
