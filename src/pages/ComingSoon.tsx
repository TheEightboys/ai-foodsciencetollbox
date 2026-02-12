import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Construction, Bell, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import apiClient from "@/lib/api/client";

interface ComingSoonProps {
  title: string;
  description: string;
}

const ComingSoon = ({ title, description }: ComingSoonProps) => {
  const [isNotifying, setIsNotifying] = useState(false);
  const [notified, setNotified] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  const handleNotifyMe = async () => {
    if (!user) {
      toast({
        title: "Sign in required",
        description: "Please sign in to be notified when this feature is available.",
        variant: "destructive",
      });
      return;
    }

    setIsNotifying(true);
    try {
      await apiClient.post('/notifications/feature-request/', {
        feature_name: title,
        user_email: user.email,
      });
      
      setNotified(true);
      toast({
        title: "You're on the list!",
        description: `We'll email you at ${user.email} when ${title} is available.`,
      });
    } catch (error: any) {
      toast({
        title: "Failed to save notification",
        description: error?.response?.data?.message || "Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsNotifying(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full text-center">
          <CardContent className="pt-8 pb-8 space-y-6">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
              <Construction className="w-8 h-8 text-primary" />
            </div>
            <div className="space-y-2">
              <h1 className="font-serif text-2xl font-bold text-foreground">
                {title}
              </h1>
              <p className="text-muted-foreground">
                {description}
              </p>
            </div>
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-3">
                This feature is currently under development and will be available soon.
              </p>
              <Button 
                variant={notified ? "default" : "outline"} 
                className="w-full"
                onClick={handleNotifyMe}
                disabled={isNotifying || notified}
              >
                {notified ? (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    You'll Be Notified
                  </>
                ) : (
                  <>
                    <Bell className="w-4 h-4 mr-2" />
                    {isNotifying ? "Saving..." : "Notify Me When Available"}
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default ComingSoon;
