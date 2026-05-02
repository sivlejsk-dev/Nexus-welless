import { Sidebar } from "@/components/layout/sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      {/* ml-64 only on desktop where sidebar is visible; pb-16 on mobile for bottom nav */}
      <main className="flex-1 md:ml-64 pb-16 md:pb-0 md:p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
