import { Sidebar } from "@/components/layout/sidebar";
import { NexusFab } from "@/components/ui/nexus-fab";

interface AppShellProps {
  children: React.ReactNode;
  /** Pass true for pages that manage their own padding (e.g. Console) */
  noPadding?: boolean;
}

export default function AppShell({ children, noPadding = false }: AppShellProps) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className={`flex-1 md:ml-64 pb-20 md:pb-0 overflow-y-auto ${noPadding ? "" : "md:p-8 p-4"}`}>
        {children}
      </main>
      <NexusFab />
    </div>
  );
}
