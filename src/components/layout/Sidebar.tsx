import { useState } from "react";
import { NavLink } from "@/components/NavLink";
import {
  LayoutDashboard,
  BookOpen,
  Target,
  Clock,
  X,
  Palette,
  FlaskConical,
  Presentation,
  FileText,
  CheckSquare,
  Mic,
  StickyNote,
  ChevronDown,
  ChevronRight,
  ClipboardCheck,
  FileQuestion,
  PenTool,
  BookMarked,
  Lightbulb,
  User,
  CreditCard,
  HelpCircle,
  Mail,
  FileText as FileTextIcon,
  Shield,
  Image,
  FileCheck,
  Utensils,
  Tag,
  Smile,
  MessageSquare,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import logo from "@/assets/logo.png";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavGroup {
  title: string;
  items: {
    title: string;
    href: string;
    icon: React.ComponentType<{ className?: string }>;
  }[];
}

const navGroups: NavGroup[] = [
  {
    title: "Starter Tools",
    items: [
      { title: "Learning Objectives Generator", href: "/objectives", icon: Target },
      { title: "Lesson Starter Generator", href: "/lesson-starter", icon: BookOpen },
      { title: "Discussion Questions Generator", href: "/check-in", icon: MessageSquare },
      { title: "Lesson Plan Generator", href: "/lesson-plan", icon: ClipboardCheck },
      { title: "Multiple Choice Quiz Generator", href: "/quiz", icon: FileQuestion },
      { title: "Key Terms and Definitions Generator", href: "/key-terms", icon: BookMarked },
    ],
  },
  {
    title: "Pro Tools",
    items: [
      { title: "Required Reading Generator", href: "/required-reading", icon: BookOpen },
      { title: "Slide Generator", href: "/slides", icon: Presentation },
      { title: "Worksheet Generator", href: "/worksheet", icon: FileText },
      { title: "Rubric Generator", href: "/rubric", icon: CheckSquare },
      { title: "Food Science Laboratory Generator", href: "/lab", icon: FlaskConical },
      { title: "Image Generator", href: "/image-generator", icon: Image },
      { title: "Project Ideas Generator", href: "/project-ideas", icon: Lightbulb },
      { title: "Project Proposal Generator", href: "/project-proposal", icon: FileCheck },
      { title: "Recipe Generator", href: "/recipe", icon: Utensils },
      { title: "Nutrition Label Generator", href: "/nutrition-label", icon: Tag },
      { title: "Teacher Jokes Generator", href: "/teacher-jokes", icon: Smile },
      { title: "Ask Courtney", href: "/ask-courtney", icon: MessageSquare },
    ],
  },
  {
    title: "Support",
    items: [
      { title: "FAQ", href: "/account/help", icon: HelpCircle },
      { title: "Contact Support", href: "/account/contact", icon: Mail },
    ],
  },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({
    "Starter Tools": true,
    "Pro Tools": true,
    "Support": false,
  });

  const toggleGroup = (title: string) => {
    setOpenGroups((prev) => ({
      ...prev,
      [title]: !prev[title],
    }));
  };

  return (
    <aside
      className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-sidebar border-r border-sidebar-border
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
      `}
    >
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="p-6 border-b border-sidebar-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={logo} alt="Food Science Toolbox" className="w-10 h-10 object-contain" />
              <div>
                <h1 className="font-semibold text-sidebar-foreground text-sm leading-tight">
                  Food Science Toolbox
                </h1>
                <p className="text-xs text-muted-foreground">AI Teaching Assistant</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={onClose}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {/* Dashboard Link - Single item, not in a group */}
          <NavLink
            to="/dashboard"
            className="flex items-center gap-3 px-4 py-2 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-200 text-sm mb-2 font-medium"
            activeClassName="bg-sidebar-accent text-sidebar-primary font-medium"
            onClick={onClose}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Dashboard</span>
          </NavLink>
          
          {/* Grouped Navigation */}
          {navGroups.map((group) => (
            <Collapsible
              key={group.title}
              open={openGroups[group.title]}
              onOpenChange={() => toggleGroup(group.title)}
            >
              <CollapsibleTrigger asChild>
                <button className="flex items-center justify-between w-full px-4 py-2 text-sm font-medium text-sidebar-foreground/80 hover:text-sidebar-foreground transition-colors">
                  <span>{group.title}</span>
                  {openGroups[group.title] ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-1 mt-1">
                {group.items.map((item) => (
                  <NavLink
                    key={item.href}
                    to={item.href}
                    className="flex items-center gap-3 px-4 py-2 pl-8 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-200 text-sm font-medium"
                    activeClassName="bg-sidebar-accent text-sidebar-primary font-medium"
                    onClick={onClose}
                    title={item.title === "FAQ" || item.title === "Contact Support" ? "admin@foodsciencetoolbox.com" : undefined}
                  >
                    <item.icon className="w-4 h-4" />
                    <span>{item.title}</span>
                  </NavLink>
                ))}
              </CollapsibleContent>
            </Collapsible>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-sidebar-border">
          <div className="space-y-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-2 flex-wrap">
              <span>© Food Science Toolbox</span>
              <span>•</span>
              <a href="/legal/terms-of-service" className="hover:text-foreground transition-colors">
                Terms of Service
              </a>
              <span>•</span>
              <a href="/legal/privacy-policy" className="hover:text-foreground transition-colors">
                Privacy Policy
              </a>
              <span>•</span>
              <a href="/legal/acceptable-use" className="hover:text-foreground transition-colors">
                Acceptable Use Policy
              </a>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}