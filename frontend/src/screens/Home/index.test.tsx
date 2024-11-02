import { render, screen } from "@testing-library/react";
import Home from "./index";

describe("Home", () => {
  it("renders the home page", () => {
    render(<Home />);

    // Add your test assertions here based on what's in your Home component
    // For example, if there's a heading:
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });
});
