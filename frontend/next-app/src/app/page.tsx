"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, FileText, Settings, User, Send, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { createProject, getRecentProjects } from '@/lib/api';

type Project = {
  id: string;
  name: string;
  problem_statement: string;
  created_at: string;
};

import { Sidebar } from "@/components/Sidebar";

export default function Home() {
  const router = useRouter();
  const [productIdea, setProductIdea] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  useEffect(() => {
    async function fetchProjects() {
      try {
        const data = await getRecentProjects(10);
        setProjects(data);
      } catch (err) {
        console.error("Failed to load projects", err);
      } finally {
        setLoadingProjects(false);
      }
    }
    fetchProjects();
  }, []);

  const handleSendMessage = async () => {
    if (!productIdea.trim()) return;

    try {
      setIsSubmitting(true);
      const project = await createProject(productIdea);
      router.push(`/phases/all?projectId=${project.id}`);
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Failed to create project. Please ensure backend is running.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#FDFCFB] text-foreground">
      <Sidebar />
      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-8 py-16">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-semibold mb-4">
              What product would you like to develop today?
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Describe your product idea in detail, and I'll guide you through a structured engineering
              workflow including functional decomposition, morphological analysis, and risk assessment.
            </p>
          </div>

          {/* Input Area */}
          <Card className="mb-8">
            <CardContent className="p-6">
              <Textarea
                placeholder="Describe your product idea..."
                value={productIdea}
                onChange={(e) => setProductIdea(e.target.value)}
                className="min-h-[300px] resize-none text-base border-0 focus-visible:ring-0 p-4"
              />
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
                <div className="text-sm text-muted-foreground">
                  {productIdea.length} characters
                </div>
                <Button
                  onClick={handleSendMessage}
                  disabled={!productIdea.trim() || isSubmitting}
                  size="lg"
                  className="gap-2"
                >
                  <Send className="h-4 w-4" />
                  {isSubmitting ? 'Creating...' : 'Send Message'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recent Projects Section */}
          <div>
            <h2 className="text-sm font-medium text-muted-foreground uppercase mb-4">
              Recent Projects
            </h2>
            {loadingProjects ? (
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <Clock className="w-4 h-4 animate-spin" /> Loading projects...
              </div>
            ) : projects.length === 0 ? (
              <div className="text-sm text-muted-foreground bg-accent/30 p-4 rounded-lg border border-border">
                You haven't created any projects yet. Describe your idea above to get started!
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {projects.slice(0, 4).map((project) => (
                  <Card
                    key={project.id}
                    onClick={() => router.push(`/phases/all?projectId=${project.id}`)}
                    className="hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <CardContent className="p-5">
                      <div className="flex items-start gap-3">
                        <FileText className="h-5 w-5 text-primary mt-1" />
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium mb-1 truncate">
                            {project.problem_statement || 'Untitled Project'}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {new Date(project.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
