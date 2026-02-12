import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ArrowLeft, User, Mail, Loader2, Save } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { authService } from '@/lib/api/auth';
import { useToast } from '@/hooks/use-toast';

export default function ProfileSettings() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return;
      
      setLoading(true);
      try {
        const profile = await authService.getProfile();
        setDisplayName(profile.display_name || `${profile.first_name} ${profile.last_name}`.trim() || '');
        setEmail(profile.email || user.email || '');
      } catch (error) {
        // Error handled silently
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [user]);

  const handleSave = async () => {
    if (!user) return;
    
    setSaving(true);
    try {
      const [firstName, ...lastNameParts] = displayName.split(' ');
      const lastName = lastNameParts.join(' ') || '';
      
      await authService.updateProfile({
        first_name: firstName || '',
        last_name: lastName,
        display_name: displayName,
      });

      toast({
        title: 'Profile updated',
        description: 'Your profile has been saved successfully.',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update profile.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-full">
                <User className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle>Profile Settings</CardTitle>
                <CardDescription>Manage your account information</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="displayName">Display Name</Label>
                  <Input
                    id="displayName"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="Enter your display name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      value={email}
                      disabled
                      className="bg-muted"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Email cannot be changed. Contact support if needed.
                  </p>
                </div>

                <Button onClick={handleSave} disabled={saving} className="w-full">
                  {saving ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
