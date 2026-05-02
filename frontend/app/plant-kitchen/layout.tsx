import { Sidebar } from "@/components/layout/sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 md:ml-64 pb-16 md:pb-0 md:p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
