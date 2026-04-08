"use client";
import React, { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Users, Search, Activity } from "lucide-react";

const MOCK_PATIENTS = [
  { id: "P001", name: "Sarah Jenkins", age: 34, condition: "Hypertension", status: "Active", lastVisit: "2026-04-01" },
  { id: "P002", name: "Michael Chen", age: 52, condition: "Type 2 Diabetes", status: "Critical", lastVisit: "2026-04-05" },
  { id: "P003", name: "Emma Watson", age: 28, condition: "Anxiety Disorder", status: "Stable", lastVisit: "2026-03-28" },
  { id: "P004", name: "David Miller", age: 45, condition: "Post-op Recovery", status: "Monitoring", lastVisit: "2026-04-03" },
  { id: "P005", name: "Alice Brown", age: 61, condition: "Cardiomegaly", status: "Active", lastVisit: "2026-03-20" },
];

export default function DoctorPatientsPage() {
  const [search, setSearch] = useState("");
  const filtered = MOCK_PATIENTS.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.condition.toLowerCase().includes(search.toLowerCase())
  );

  const statusColor: Record<string, string> = {
    Active: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    Critical: "bg-red-500/20 text-red-400 border-red-500/30",
    Stable: "bg-green-500/20 text-green-400 border-green-500/30",
    Monitoring: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  };

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem><BreadcrumbLink href="/doctor/dashboard">Doctor Portal</BreadcrumbLink></BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem><BreadcrumbPage>My Patients</BreadcrumbPage></BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <main className="p-6 space-y-6">
          <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2"><Users className="w-7 h-7 text-primary" /> My Patients</h1>
              <p className="text-muted-foreground mt-1">{filtered.length} patients found</p>
            </div>
            <div className="relative max-w-xs w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search patients..." className="pl-9" />
            </div>
          </div>
          <Card>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead className="border-b bg-muted/30">
                  <tr>
                    {["Patient ID", "Name", "Age", "Condition", "Last Visit", "Status", "Actions"].map(h => (
                      <th key={h} className="text-left p-4 font-medium text-muted-foreground">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filtered.map(p => (
                    <tr key={p.id} className="hover:bg-muted/20 transition-colors">
                      <td className="p-4 font-mono text-xs text-muted-foreground">{p.id}</td>
                      <td className="p-4 font-semibold">{p.name}</td>
                      <td className="p-4">{p.age}</td>
                      <td className="p-4">{p.condition}</td>
                      <td className="p-4 text-muted-foreground">{p.lastVisit}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-xs border ${statusColor[p.status] || ""}`}>{p.status}</span>
                      </td>
                      <td className="p-4">
                        <Button size="sm" variant="outline" className="gap-1">
                          <Activity className="w-3 h-3" /> View
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}