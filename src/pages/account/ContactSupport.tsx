import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowLeft, Mail, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { authService } from '@/lib/api/auth';

export default function ContactSupport() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

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
                <Mail className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle>Contact Support</CardTitle>
                <CardDescription>Send us a message and we'll get back to you as soon as possible</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                if (!message.trim()) {
                  toast({
                    title: 'Message required',
                    description: 'Please enter your message.',
                    variant: 'destructive',
                  });
                  return;
                }

                setIsSubmitting(true);
                try {
                  await authService.contactSupport(
                    subject.trim() || 'Support Request',
                    message.trim()
                  );
                  toast({
                    title: 'Message sent!',
                    description: 'Your message has been sent successfully. We will get back to you soon.',
                  });
                  setSubject('');
                  setMessage('');
                } catch (error: any) {
                  const errorMessage = error?.response?.data?.error || error?.response?.data?.message || 'Failed to send message. Please try again.';
                  toast({
                    title: 'Failed to send',
                    description: errorMessage,
                    variant: 'destructive',
                  });
                } finally {
                  setIsSubmitting(false);
                }
              }}
              className="space-y-4"
            >
              <div className="space-y-2">
                <Label htmlFor="email">Your Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="bg-muted"
                />
                <p className="text-xs text-muted-foreground">
                  This is the email address associated with your account.
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="subject">Subject (Optional)</Label>
                <Input
                  id="subject"
                  type="text"
                  placeholder="Brief description of your issue"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  disabled={isSubmitting}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="message">Message *</Label>
                <Textarea
                  id="message"
                  placeholder="Please describe your issue or question in detail..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  disabled={isSubmitting}
                  rows={8}
                  className="resize-none"
                  required
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button type="submit" disabled={isSubmitting || !message.trim()} className="w-full sm:w-auto">
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="h-4 w-4 mr-2" />
                      Send Message
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

