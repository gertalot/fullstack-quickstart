import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, Mock, vi } from "vitest";
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
    (fetch as Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        message: "TEMPLATE_PROJECT_NAME API is healthy!",
        uptime: { days: 1, hours: 2, minutes: 3, seconds: 4 },
      }),
    });
    render(<Home />);
    await waitFor(() => {
      expect(screen.getByText("TEMPLATE_PROJECT_NAME API is healthy!")).toBeInTheDocument();
      expect(screen.getByText(/Live since 1 days, 2 hours, 3 minutes/)).toBeInTheDocument();
    });
  });

  it("renders error message on fetch failure", async () => {
    (fetch as Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: "Internal Server Error" }),
    });
    render(<Home />);
    await waitFor(() => {
      const errorMessages = screen.getAllByText("Internal Server Error");
      expect(errorMessages.length).toBe(2);
      expect(screen.getByText(/Status: 500/)).toBeInTheDocument();
    });
  });
}); 