import AppShell from "@/components/layout/app-shell";
export default function Layout({ children }: { children: React.ReactNode }) {
  return <AppShell noPadding>{children}</AppShell>;
}
