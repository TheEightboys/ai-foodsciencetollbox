import { useNavigate } from "react-router-dom";
import { Menu, User, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "./ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { useProfile } from "@/hooks/useProfile";
import { useToast } from "@/hooks/use-toast";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const { profile, remainingGenerations, isUnlimited } = useProfile();
  const { toast } = useToast();

  const handleSignOut = async () => {
    try {
      await signOut();
      toast({
        title: "Signed out",
        description: "You have been signed out successfully.",
      });
      navigate("/");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sign out. Please try again.",
        variant: "destructive",
      });
    }
  };

  const displayName = profile?.display_name || "Teacher";

  return (
    <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-lg border-b border-border">
      <div className="flex items-center justify-between h-16 px-4 md:px-6">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
        >
          <Menu className="w-5 h-5" />
        </Button>

        {/* Spacer for desktop */}
        <div className="hidden lg:block" />

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Generation counter */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-secondary rounded-full">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span className="text-sm text-secondary-foreground">
              {isUnlimited ? (
                <span className="font-semibold">Unlimited</span>
              ) : (
                <>
                  <span className="font-semibold">{remainingGenerations}</span> generations left
                </>
              )}
            </span>
          </div>

          {/* Theme toggle */}
          <ThemeToggle />

          {/* Profile dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                  <User className="w-4 h-4 text-primary-foreground" />
                </div>
                <span className="hidden md:inline text-sm font-medium">
                  {displayName}
                </span>
                <ChevronDown className="w-4 h-4 text-muted-foreground" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate('/account/profile')}>
                Profile Settings
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/account/billing')}>
                Billing
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/account/help')}>
                Help & Support
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                className="text-destructive focus:text-destructive"
                onClick={handleSignOut}
              >
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
