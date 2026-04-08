"use client";

import React, { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Activity, Brain, Bone, FileText, Upload, RefreshCcw, Download, CheckCircle2, AlertCircle, Search, Microscope } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth";
import { PostScanActionPanel } from "@/features/appointments/components/PostScanActionPanel";
import { BookingFlow } from "@/features/appointments/components/BookingFlow";
import { AppointmentMode } from "@/features/appointments/types/appointment";

const API_BASE = "http://localhost:8000";

type Prediction = [string, number];

interface AnalysisResult {
  disease?: string;
  confidence?: number;
  predictions?: Record<string, number>;
  report?: string;
  model_used?: string;
  input_type?: string;
  image_url?: string;
  classifications?: any;
  top_prediction?: string;
  top_confidence?: number;
}

export default function NeuroVisionPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("chest");
  const [file, setFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageDimensions, setImageDimensions] = useState<{w: number, h: number} | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [reportText, setReportText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [genReport, setGenReport] = useState(true);
  const [fastMode, setFastMode] = useState(false);
  const [showBookingFlow, setShowBookingFlow] = useState(false);
  const [bookingMode, setBookingMode] = useState<AppointmentMode | undefined>(undefined);

  // Patient Info
  const [patientName, setPatientName] = useState(user?.name || '');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');

  const samples = [
    {
      title: "Pneumonia Case",
      text: "Patient presents with acute chest pain and shortness of breath. Chest X-ray shows bilateral lower lobe opacities consistent with pneumonia. No pneumothorax or pleural effusion noted. Cardiomegaly is present."
    },
    {
      title: "Fracture Suspect",
      text: "Patient fell from a height. Pain and swelling in the right distal forearm. Visual deformity present. X-ray required to rule out Colles' fracture."
    }
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setResult(null);
      setError(null);
      setPreviewLoading(true);
      setImageDimensions(null);
      // Use free browser-native FileReader for live preview
      const reader = new FileReader();
      reader.onload = (ev) => {
        const src = ev.target?.result as string;
        setImagePreview(src);
        // Load image to get dimensions
        const img = new Image();
        img.onload = () => {
          setImageDimensions({ w: img.naturalWidth, h: img.naturalHeight });
          setPreviewLoading(false);
        };
        img.src = src;
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const runAnalysis = async () => {
    if (activeTab !== "text" && activeTab !== "general" && !file) {
      setError("Please upload an image first.");
      return;
    }
    if (activeTab === "text" && !reportText.trim()) {
      setError("Please enter report text.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    if (file) formData.append("image", file);
    if (reportText) formData.append("report_text", reportText);
    formData.append("generate_report", genReport.toString());
    formData.append("fast_mode", fastMode.toString());
    if (activeTab === "general") formData.append("use_comprehensive", "true");
    
    // Add patient demographics
    formData.append("patient_name", patientName || "Not Provided");
    formData.append("patient_age", patientAge || "N/A");
    formData.append("patient_gender", patientGender || "N/A");

    let endpoint = `${API_BASE}/api/classify`;
    if (activeTab === "chest") endpoint = `${API_BASE}/api/classify/chest`;
    else if (activeTab === "bone") endpoint = `${API_BASE}/api/classify/bone`;
    else if (activeTab === "brain") endpoint = `${API_BASE}/api/classify/brain`;
    else if (activeTab === "text") endpoint = `${API_BASE}/api/classify/text`;
    else if (activeTab === "general") endpoint = `${API_BASE}/api/classify`;

    try {
      let response;
      if (activeTab === "text") {
        response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            report_text: reportText,
            fast_mode: fastMode,
            patient_name: patientName || "Not Provided",
            patient_age: patientAge || "N/A",
            patient_gender: patientGender || "N/A"
          }),
        });
      } else {
        response = await fetch(endpoint, {
          method: "POST",
          body: formData,
        });
      }

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    if (!result) return;
    try {
      const scanTypeMap: Record<string, string> = {
        chest: "Chest X-Ray",
        brain: "Brain MRI",
        bone: "Bone X-Ray",
        general: "Medical Scan",
        text: "Laboratory Report",
      };

      const disease = result.disease || result.top_prediction || "Unknown";
      const confidence = result.confidence != null
        ? result.confidence
        : result.top_confidence != null
          ? result.top_confidence <= 1 ? result.top_confidence * 100 : result.top_confidence
          : 0;
      const reportText = result.report || "";

      const formData = new FormData();
      formData.append("scan_type", scanTypeMap[activeTab] || "Medical Scan");
      formData.append("disease", String(disease));
      formData.append("confidence", String(confidence));
      formData.append("report_text", reportText);
      formData.append("patient_name", patientName || "Not Provided");
      formData.append("patient_age", patientAge || "N/A");
      formData.append("patient_gender", patientGender || "N/A");

      const response = await fetch(`${API_BASE}/api/report/download`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Failed to generate PDF");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Synapse_Medical_Report_${scanTypeMap[activeTab]?.replace(/ /g, "_") || activeTab}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert("Failed to download PDF report: " + err.message);
    }
  };


  const getConfidencePairs = (res: AnalysisResult): Prediction[] => {
    const classifications = res.classifications as Record<string, any> || {};
    if (res.predictions) {
      return Object.entries(res.predictions as Record<string, number>)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    }
    if (classifications) {
      if (activeTab === "chest" && classifications.custom_chest) {
        return Object.entries(classifications.custom_chest.predictions || {}).sort((a, b: any) => (b[1] as number) - (a[1] as number)) as Prediction[];
      }
      if (activeTab === "brain" && classifications.brain_tumor) {
        return Object.entries(classifications.brain_tumor.predictions || {}).sort((a, b: any) => (b[1] as number) - (a[1] as number)) as Prediction[];
      }
      // General/Bone fallback
      const medsiglip = classifications.medsiglip || {};
      if (medsiglip.predictions) {
        return Object.entries(medsiglip.predictions as Record<string, number>).sort((a, b) => b[1] - a[1]).slice(0, 5);
      }
    }
    return [];
  };

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-slate-950 text-slate-50">
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-white/5 px-4 transition-[width,height] ease-linear">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>NeuroVision AI</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-6xl space-y-8">
            <div className="flex flex-col md:flex-row justify-between md:items-end gap-6">
              <div className="space-y-2">
                <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-emerald-300 to-cyan-400 bg-clip-text text-transparent">
                  NeuroVision Diagnostics
                </h1>
                <p className="text-slate-400">
                  Precision Medical AI for automated radiological screening.
                </p>
              </div>
              <div className="bg-slate-900/80 border border-white/5 rounded-xl p-4 flex items-center gap-6 shadow-xl backdrop-blur-md">
                <div className="flex items-center space-x-2">
                  <Switch id="gen-report" checked={genReport} onCheckedChange={setGenReport} />
                  <Label htmlFor="gen-report" className="text-xs font-semibold uppercase tracking-wider text-slate-400">PDF Report</Label>
                </div>
                <Separator orientation="vertical" className="h-6" />
                <div className="flex items-center space-x-2">
                  <Switch id="fast-mode" checked={fastMode} onCheckedChange={setFastMode} />
                  <div className="flex flex-col">
                    <Label htmlFor="fast-mode" className="text-[10px] font-bold uppercase tracking-wider text-blue-400 leading-none">Fast Mode</Label>
                    <span className="text-[8px] text-slate-500 uppercase mt-1">Turbo Results</span>
                  </div>
                </div>
                <Separator orientation="vertical" className="h-6" />
                <div className="flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                   <span className="text-xs font-semibold text-emerald-400 uppercase tracking-widest">Models Online</span>
                </div>
              </div>
            </div>

            <Tabs defaultValue="chest" onValueChange={(v) => { setActiveTab(v); setFile(null); setResult(null); setError(null); }} className="w-full">
              <TabsList className="grid w-full grid-cols-5 bg-slate-900/50 p-1.5 rounded-2xl border border-white/5 h-14">
                <TabsTrigger value="chest" className="rounded-xl data-[state=active]:bg-blue-600 transition-all font-medium">
                  <Activity className="w-4 h-4 mr-2" />
                  Chest
                </TabsTrigger>
                <TabsTrigger value="bone" className="rounded-xl data-[state=active]:bg-blue-600 transition-all font-medium">
                  <Bone className="w-4 h-4 mr-2" />
                  Bone
                </TabsTrigger>
                <TabsTrigger value="brain" className="rounded-xl data-[state=active]:bg-blue-600 transition-all font-medium">
                  <Brain className="w-4 h-4 mr-2" />
                  Brain
                </TabsTrigger>
                <TabsTrigger value="text" className="rounded-xl data-[state=active]:bg-blue-600 transition-all font-medium">
                  <FileText className="w-4 h-4 mr-2" />
                  Reports
                </TabsTrigger>
                <TabsTrigger value="general" className="rounded-xl data-[state=active]:bg-blue-600 transition-all font-medium">
                  <Microscope className="w-4 h-4 mr-2" />
                  General
                </TabsTrigger>
              </TabsList>

              <div className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Input Column (Lg: 7) */}
                <div className="lg:col-span-7 space-y-6">
                  <Card className="bg-slate-900/40 border-white/10 backdrop-blur-2xl shadow-2xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-5">
                       <Search className="w-32 h-32" />
                    </div>
                    <CardHeader className="relative z-10">
                      <CardTitle className="text-2xl font-bold flex items-center">
                         {activeTab === "chest" && "🫁 Chest X-Ray Analysis"}
                         {activeTab === "bone" && "🦴 Orthopedic Analysis"}
                         {activeTab === "brain" && "🧠 Brain MRI Screening"}
                         {activeTab === "text" && "📝 Report NLP Engine"}
                         {activeTab === "general" && "🔬 Multi-Modal Analysis"}
                      </CardTitle>
                      <CardDescription className="text-slate-400">
                        Primary Diagnostic: {activeTab === "chest" ? "CustomNet121 Ensemble" : activeTab === "brain" ? "InceptionV3 Ensemble" : "MedSigLIP Dual-Verification"}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6 relative z-10">
                      {/* Patient Info Panel */}
                      <div className="bg-slate-950/60 rounded-xl border border-white/5 p-4">
                        <p className="text-[10px] font-extrabold text-blue-400 uppercase tracking-[0.2em] mb-3">Patient Information</p>
                        <div className="grid grid-cols-3 gap-3">
                          <div>
                            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Full Name</Label>
                            <Input 
                              value={patientName}
                              onChange={e => setPatientName(e.target.value)}
                              placeholder="e.g. Swayam Patel"
                              className="mt-1 bg-slate-900/60 border-white/5 text-sm h-9 placeholder:text-slate-600"
                            />
                          </div>
                          <div>
                            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Age</Label>
                            <Input 
                              value={patientAge}
                              onChange={e => setPatientAge(e.target.value)}
                              placeholder="e.g. 25"
                              className="mt-1 bg-slate-900/60 border-white/5 text-sm h-9 placeholder:text-slate-600"
                            />
                          </div>
                          <div>
                            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Gender</Label>
                            <select
                              value={patientGender}
                              onChange={e => setPatientGender(e.target.value)}
                              className="mt-1 w-full bg-slate-900/60 border border-white/5 text-sm h-9 rounded-md px-3 text-slate-200 focus:ring-2 focus:ring-blue-500/40 outline-none"
                            >
                              <option value="">Select</option>
                              <option value="Male">Male</option>
                              <option value="Female">Female</option>
                              <option value="Other">Other</option>
                            </select>
                          </div>
                        </div>
                      </div>

                      {activeTab !== "text" && activeTab !== "general" && (
                        <div className="space-y-4">
                          <div 
                            className="border-2 border-dashed border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center space-y-4 hover:border-blue-500/40 transition-all bg-slate-950/40 cursor-pointer group/upload shadow-inner"
                            onClick={() => document.getElementById('file-upload')?.click()}
                          >
                            <div className="w-16 h-16 rounded-2xl bg-blue-500/5 flex items-center justify-center group-hover/upload:scale-110 transition-transform">
                              <Upload className="w-8 h-8 text-blue-400" />
                            </div>
                            <div className="text-center">
                              <p className="text-lg font-semibold">{file ? file.name : "Select Medical Scan"}</p>
                              <p className="text-sm text-slate-500 mt-1">Supporting frontline images, DICOM exports</p>
                            </div>
                            <Input 
                              id="file-upload" 
                              type="file" 
                              className="hidden" 
                              onChange={handleFileChange}
                              accept="image/*"
                            />
                          </div>
                          {/* Live Image Preview using FileReader (browser-native, free) */}
                          {(imagePreview || previewLoading) && (
                            <div className="rounded-2xl border border-blue-500/20 bg-slate-950/60 overflow-hidden">
                              <div className="flex items-center justify-between px-4 py-2 border-b border-white/5">
                                <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Live Preview</span>
                                {imageDimensions && (
                                  <span className="text-xs text-slate-500">{imageDimensions.w} × {imageDimensions.h}px • {file ? (file.size/1024).toFixed(0) : 0} KB</span>
                                )}
                              </div>
                              <div className="relative p-4 flex items-center justify-center min-h-[200px]">
                                {previewLoading ? (
                                  <div className="flex flex-col items-center gap-3">
                                    <RefreshCcw className="w-8 h-8 animate-spin text-blue-400" />
                                    <span className="text-sm text-slate-400">Loading preview...</span>
                                  </div>
                                ) : imagePreview ? (
                                  <img
                                    src={imagePreview}
                                    alt="Medical scan preview"
                                    className="max-h-64 max-w-full rounded-xl object-contain shadow-2xl ring-1 ring-white/10"
                                  />
                                ) : null}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {activeTab === "general" && (
                         <div className="grid grid-cols-2 gap-4 h-48">
                            <div 
                              className="border border-white/5 rounded-xl flex flex-col items-center justify-center space-y-2 bg-slate-950/40 hover:bg-slate-900 transition-colors cursor-pointer"
                              onClick={() => document.getElementById('file-upload-gen')?.click()}
                            >
                               <Upload className="w-6 h-6 text-blue-400" />
                               <span className="text-sm font-medium">{file ? "Image Attached" : "Upload Image"}</span>
                               <Input id="file-upload-gen" type="file" className="hidden" onChange={handleFileChange} />
                            </div>
                            <Textarea 
                               placeholder="Optional: Add clinical notes to correlate with image..." 
                               className="bg-slate-950/40 border-white/5 resize-none h-full pt-4"
                               value={reportText}
                               onChange={(e) => setReportText(e.target.value)}
                            />
                         </div>
                      )}

                      {(activeTab === "text") && (
                        <div className="space-y-4">
                          <Textarea 
                            placeholder="Paste medical report or patient history here..." 
                            className="bg-slate-950/40 border-white/5 min-h-[250px] text-base leading-relaxed p-6"
                            value={reportText}
                            onChange={(e) => setReportText(e.target.value)}
                          />
                          <div className="flex gap-2">
                             {samples.map((s, i) => (
                               <Button key={i} variant="ghost" className="text-xs text-slate-400 hover:text-white h-8 px-3 border border-white/5" onClick={() => setReportText(s.text)}>
                                 Sample: {s.title}
                               </Button>
                             ))}
                          </div>
                        </div>
                      )}

                      {error && (
                        <div className="flex items-center gap-3 text-red-100 text-sm bg-red-500/10 p-4 rounded-xl border border-red-500/20">
                          <AlertCircle className="w-5 h-5 text-red-500" />
                          {error}
                        </div>
                      )}
                    </CardContent>
                    <CardFooter className="pt-2 pb-8">
                      <Button 
                        onClick={runAnalysis} 
                        className="w-full py-7 text-xl font-bold bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:scale-[1.01] active:scale-[0.99] transition-all shadow-2xl shadow-blue-900/30 rounded-2xl"
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <RefreshCcw className="w-6 h-6 mr-3 animate-spin" />
                            Synchronizing AI Models...
                          </>
                        ) : (
                          <>
                            <Activity className="w-6 h-6 mr-3" />
                            Perform Diagnosis
                          </>
                        )}
                      </Button>
                    </CardFooter>
                  </Card>
                </div>

                {/* Results Column (Lg: 5) */}
                <div className="lg:col-span-5 space-y-6">
                  <Card className="bg-slate-900/40 border-white/10 backdrop-blur-2xl shadow-2xl h-full flex flex-col min-h-[500px]">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg font-bold flex items-center text-slate-300">
                        <Microscope className="w-4 h-4 mr-2" />
                        AI Clinical Analysis
                      </CardTitle>
                    </CardHeader>
                    <Separator className="bg-white/5 mx-6 w-[calc(100%-48px)]" />
                    <CardContent className="flex-1 overflow-y-auto py-6">
                      <AnimatePresence mode="wait">
                        {!result && !loading && (
                          <motion.div 
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                            className="h-full flex flex-col items-center justify-center text-slate-600 space-y-6 py-20"
                          >
                            <div className="relative">
                               <RefreshCcw className="w-20 h-20 opacity-5" />
                               <CheckCircle2 className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 opacity-20" />
                            </div>
                            <p className="text-sm font-medium tracking-wide uppercase italic">System Ready for Input</p>
                          </motion.div>
                        )}

                        {loading && (
                          <motion.div 
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                            className="h-full flex flex-col items-center justify-center space-y-10 py-16"
                          >
                            <div className="relative">
                              <div className="w-32 h-32 border-4 border-blue-500/10 border-t-blue-500 rounded-full animate-spin"></div>
                              <Microscope className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 text-blue-400" />
                            </div>
                            <div className="text-center space-y-3">
                              <p className="text-lg font-bold text-blue-300 tracking-tight">Neural Decoding Active</p>
                              <div className="flex gap-1 justify-center">
                                 <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                 <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                 <span className="w-1.5 h-1.5 bg-blue-300 rounded-full animate-bounce"></span>
                              </div>
                            </div>
                          </motion.div>
                        )}

                        {result && (
                          <motion.div 
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="space-y-8"
                          >
                            <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/5 border border-emerald-500/20 rounded-2xl p-6 relative overflow-hidden group/result">
                              <div className="absolute -top-4 -right-4 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl group-hover/result:scale-150 transition-transform"></div>
                              <div className="relative z-10 flex flex-col gap-1">
                                <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-[0.2em]">Verified Diagnosis</span>
                                <h3 className="text-3xl font-black text-white leading-tight">
                                  {result.disease || (result.classifications?.brain_tumor?.disease) || "Analysis Finalized"}
                                </h3>
                                <div className="mt-4 flex items-end justify-between">
                                   <div className="flex flex-col">
                                      <span className="text-[10px] uppercase text-slate-400 font-bold tracking-widest leading-none">Conf. Score</span>
                                      <span className="text-4xl font-extrabold text-emerald-400">
                                         {result.confidence ? `${(result.confidence * 100).toFixed(1)}%` : 
                                          result.classifications?.brain_tumor?.confidence ? `${(result.classifications.brain_tumor.confidence * 100).toFixed(1)}%` : "N/A"}
                                      </span>
                                   </div>
                                   <div className="bg-emerald-500/20 px-3 py-1 rounded-full border border-emerald-500/20">
                                      <span className="text-[10px] font-bold text-emerald-400 uppercase">Class S</span>
                                   </div>
                                </div>
                              </div>
                            </div>

                            <div className="space-y-5">
                              <h4 className="text-[11px] font-black text-slate-500 uppercase tracking-[0.3em]">Probability Distribution</h4>
                              <div className="space-y-5">
                                {getConfidencePairs(result).map(([label, score], idx) => (
                                  <div key={idx} className="space-y-2">
                                    <div className="flex justify-between text-xs font-bold font-mono">
                                      <span className="text-slate-300 uppercase tracking-wider">{label.replace(/_/g, " ")}</span>
                                      <span className="text-blue-400">{(score * 100).toFixed(1)}%</span>
                                    </div>
                                    <Progress value={score * 100} className="h-2 bg-slate-800/50 rounded-full" />
                                  </div>
                                ))}
                              </div>
                            </div>

                            {result.report && (
                              <div className="space-y-3">
                                <h4 className="text-[11px] font-black text-slate-500 uppercase tracking-[0.3em]">Impressions & Findings</h4>
                                <div className="bg-slate-950/60 rounded-2xl p-6 border border-white/5 text-sm leading-relaxed text-slate-300 max-h-[350px] overflow-y-auto whitespace-pre-wrap font-mono custom-scrollbar border-l-2 border-l-blue-500/50">
                                  {result.report}
                                </div>
                              </div>
                            )}

                            <div className="pt-4 flex flex-col gap-3">
                              <Button 
                                onClick={downloadPDF}
                                className="w-full py-6 text-base font-bold bg-slate-900 border border-white/5 hover:bg-slate-800 transition-all rounded-xl shadow-lg"
                              >
                                <Download className="w-4 h-4 mr-2 text-blue-400" />
                                Download PDF Report
                              </Button>
                              <p className="text-[10px] text-center text-slate-500 italic">
                                Note: This AI analysis is for research assistance purposes only.
                              </p>
                              {/* ✅ Post-Scan Action Panel — additive only, no existing code modified */}
                              <PostScanActionPanel
                                onSelect={(mode) => { setBookingMode(mode); setShowBookingFlow(true); }}
                                scanType={activeTab}
                                uploadedFileName={file?.name || ''}
                              />
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </Tabs>
          </div>
        </main>
      </SidebarInset>

      {/* Booking Flow Modal — triggered by PostScanActionPanel */}
      <BookingFlowPortal
        show={showBookingFlow}
        mode={bookingMode}
        aiReport={result?.report || ''}
        scanType={activeTab}
        uploadedFileName={file?.name || ''}
        patientName={patientName}
        onClose={() => setShowBookingFlow(false)}
      />
    </SidebarProvider>
  );
}

// ─── BookingFlow Modal rendered via AnimatePresence ───────────────────────────
function BookingFlowPortal({
  show,
  mode,
  aiReport,
  scanType,
  uploadedFileName,
  patientName,
  onClose,
}: {
  show: boolean;
  mode: AppointmentMode | undefined;
  aiReport: string;
  scanType: string;
  uploadedFileName: string;
  patientName: string;
  onClose: () => void;
}) {
  return (
    <AnimatePresence>
      {show && (
        <BookingFlow
          aiReport={aiReport}
          scanType={scanType}
          uploadedFileName={uploadedFileName}
          patientName={patientName}
          initialMode={mode}
          onClose={onClose}
        />
      )}
    </AnimatePresence>
  );
}
