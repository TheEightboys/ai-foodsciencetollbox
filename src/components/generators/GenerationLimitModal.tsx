import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

interface GenerationLimitModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GenerationLimitModal({ open, onOpenChange }: GenerationLimitModalProps) {
  const navigate = useNavigate();

  const handleUpgrade = () => {
    onOpenChange(false);
    navigate("/pricing");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Generation Limit Reached</DialogTitle>
          <DialogDescription className="pt-2">
            Your available generations have been used. Upgrade your plan to continue generating content.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-start sm:flex-row sm:space-x-2">
          <Button onClick={handleUpgrade} className="w-full sm:w-auto">
            Upgrade
          </Button>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="w-full sm:w-auto"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

