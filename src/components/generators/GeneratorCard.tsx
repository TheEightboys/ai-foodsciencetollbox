import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight, Lock } from "lucide-react";

interface GeneratorCardProps {
  title: string;
  description: string;
  icon: ReactNode;
  href: string;
  isActive?: boolean;
  comingSoon?: boolean;
}

export function GeneratorCard({
  title,
  description,
  icon,
  href,
  isActive = true,
  comingSoon = false,
}: GeneratorCardProps) {
  if (comingSoon) {
    return (
      <Card className="relative overflow-hidden bg-muted/50 border-dashed opacity-70 hover:opacity-80 transition-opacity cursor-not-allowed">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center shrink-0">
              {icon}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-serif font-semibold text-foreground/60">
                  {title}
                </h3>
                <Lock className="w-3.5 h-3.5 text-muted-foreground" />
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {description}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Link to={href} className="block group">
      <Card className="h-full hover:shadow-card-hover hover:border-primary transition-all duration-300 group-hover:-translate-y-1 border-2 border-primary/50 hover:border-primary">
        <CardContent className="p-6">
          <div className="flex flex-col h-full">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center shrink-0 group-hover:from-primary/20 group-hover:to-accent/20 transition-colors">
                {icon}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-serif font-semibold text-foreground mb-1 group-hover:text-primary transition-colors">
                  {title}
                </h3>
                <p className="text-sm text-foreground/80 line-clamp-2">
                  {description}
                </p>
              </div>
            </div>
            <div className="mt-auto pt-4 border-t border-border">
              <div className="w-full px-4 py-2 rounded-lg text-primary hover:bg-primary/15 hover:text-foreground transition-all group/btn cursor-pointer">
                <div className="flex items-center justify-between">
                  <span className="transition-colors">Generate</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
