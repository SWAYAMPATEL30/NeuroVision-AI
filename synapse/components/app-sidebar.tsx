"use client";

import * as React from "react";
import {
  Activity,
  AudioWaveform,
  BookOpen,
  Bot,
  Command,
  GalleryVerticalEnd,
  Settings2,
  SquareTerminal,
  User,
} from "lucide-react";

import { NavMain } from "@/components/nav-main";
import { NavUser } from "@/components/nav-user";
import { TeamSwitcher } from "@/components/team-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import LanguageTranslationComponent from "./language";
import { ThemeSwitcher } from "./themeswitch";
import { DyslexiaFontToggle } from "./dyslexia-font-toggle";
import { useUser } from "@/lib/UserContext"; // 🔥 import the hook

const baseData = {
  teams: [
    {
      name: "NeuroVision AI",
      logo: GalleryVerticalEnd,
      plan: "Enterprise",
    },
    {
      name: "Acme Corp.",
      logo: AudioWaveform,
      plan: "Startup",
    },
    {
      name: "Evil Corp.",
      logo: Command,
      plan: "Free",
    },
  ],
};

import { useAuth } from "@/lib/auth"; // 🔥 RBAC Support

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user: supaUser } = useUser(); // 🔥 get logged in user (SupaBase fallback)
  const { user: authUser } = useAuth(); // New Auth setup
  
  const [navItems, setNavItems] = React.useState<any[]>([]);

  React.useEffect(() => {
    if (authUser?.role === 'DOCTOR') {
      setNavItems([
        {
          title: "Doctor Portal",
          url: "/doctor/dashboard",
          icon: SquareTerminal,
          isActive: true,
          items: [
            { title: "Overview", url: "/doctor/dashboard" },
            { title: "My Patients", url: "/doctor/patients" },
            { title: "Appointments", url: "/doctor/appointments" },
          ],
        },
      ]);
    } else {
      setNavItems([
        {
          title: "Playground",
          url: "",
          icon: SquareTerminal,
          isActive: true,
          items: [
            { title: "🔊 Voice Therapist", url: "/dashboard/voice" },
            { title: "🤖 MedBot AI Chat", url: "/dashboard/chatbot" },
            { title: "🧩 Activities", url: "/dashboard/games" },
            { title: "🧘 VR Connect", url: "/dashboard/panchayat" },
            { title: "📑 Resource", url: "/dashboard/resource" },
            { title: "📝 Planner", url: "/dashboard/planner" },
          ],
        },
        {
          title: "Therapist",
          url: "#",
          icon: BookOpen,
          items: [
            { title: "Monitor EEG", url: "/dashboard/theraphist" },
            { title: "📅 Book Appointment", url: "/dashboard/book-appointment" },
            { title: "Cognitive Health", url: "/dashboard/cognitive-health" },
          ],
        },
        {
          title: "NeuroVision AI",
          url: "#",
          icon: Activity,
          items: [
            { title: "Diagnostics", url: "/dashboard/neurovision" },
            { title: "🩺 Find Doctors", url: "/dashboard/doctors" },
          ],
        },
      ]);
    }
  }, [authUser]);

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={baseData.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navItems} />
        <ThemeSwitcher />
        <DyslexiaFontToggle />
      </SidebarContent>
      <SidebarFooter>
        <LanguageTranslationComponent />
        <NavUser
          user={{
            name: authUser?.name || supaUser?.user_metadata?.full_name || supaUser?.email || "Guest",
            email: authUser?.email || supaUser?.email || "",
            avatar: authUser?.photo || supaUser?.user_metadata?.avatar_url,
          }}
        />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
