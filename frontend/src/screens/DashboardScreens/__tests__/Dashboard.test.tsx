import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Dashboard from '../Dashboard';  // Adjust the import path as necessary
import '@testing-library/jest-dom';

// Mock modules as necessary
jest.mock('api/fetchStats', () => ({
  useFetchStats: jest.fn().mockReturnValue({ data: { links: {} } }),
}));
jest.mock('api/fetchLinks', () => ({
  useFetchLinks: jest.fn().mockReturnValue({ data: { links: [] }, isLoading: false, error: null }),
}));

describe('Dashboard Component', () => {
  test('renders welcome message', () => {
    render(<Dashboard />);
    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();
  });

  test('displays loading message while fetching links', () => {
    jest.mock('api/fetchLinks', () => ({
      useFetchLinks: jest.fn().mockReturnValue({ data: null, isLoading: true, error: null }),
    }));
    render(<Dashboard />);
    expect(screen.getByText(/loading links/i)).toBeInTheDocument();
  });

  test('displays stats cards', () => {
    render(<Dashboard />);
    const statsTitles = ["Total Links", "Enabled Links", "Disabled Links", "Link Visits"];
    statsTitles.forEach((title) => {
      expect(screen.getByText(title)).toBeInTheDocument();
    });
  });

  test('opens Create Link drawer when "Shorten Link" button is clicked', () => {
    render(<Dashboard />);
    const button = screen.getByText(/Shorten Link/i);
    fireEvent.click(button);
    expect(screen.getByText(/Create Link/i)).toBeInTheDocument(); // Assuming 'Create Link' is in the drawer
  });
});
