import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Home from "./page";

// Mock fetch globally
beforeEach(() => {
  global.fetch = vi.fn();
});
afterEach(() => {
  vi.resetAllMocks();
});

describe("Home page", () => {
  it("renders healthcheck message and uptime on success", async () => {
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        message: "Savour Herbs API is healthy!",
        uptime: { days: 1, hours: 2, minutes: 3, seconds: 4 },
      }),
    });
    render(<Home />);
    await waitFor(() => {
      expect(screen.getByText("Savour Herbs API is healthy!")).toBeInTheDocument();
      expect(screen.getByText(/Live since 1 days, 2 hours, 3 minutes/)).toBeInTheDocument();
    });
  });

  it("renders error message on fetch failure", async () => {
    (fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: "Internal Server Error" }),
    });
    render(<Home />);
    await waitFor(() => {
      expect(screen.getByText("Internal Server Error")).toBeInTheDocument();
      expect(screen.getByText(/Status: 500/)).toBeInTheDocument();
    });
  });
}); 