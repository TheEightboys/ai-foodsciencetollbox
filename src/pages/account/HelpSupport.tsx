import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { ArrowLeft, HelpCircle, FileText, ExternalLink } from 'lucide-react';

const faqs = [
  {
    question: 'What is the Lesson Starter Generator used for?',
    answer: 'The Lesson Starter is designed to introduce a topic, spark curiosity, and lead into a short, high-quality discussion. It provides brief context and ends with a single open-ended question. The opening script is approximately 180-200 words (1-2 minutes spoken) and the discussion question is designed to sustain at least 5 minutes of student discussion.',
  },
  {
    question: 'Is the Lesson Starter for students or teachers?',
    answer: 'The Lesson Starter has both teacher-facing and student-facing sections. The "Prior Knowledge to Connect" section is teacher-facing planning guidance. The "Teacher Opening Script" and "Discussion Question" are student-facing and designed to be delivered to students.',
  },
  {
    question: 'What is the Discussion Question Generator?',
    answer: 'The Discussion Question Generator creates standalone, content-focused questions that are meant to drive deeper thinking during or after instruction. These questions are designed to support thinking, explanation, application, or evaluation and function as thinking prompts rather than framing devices.',
  },
  {
    question: 'How should teachers use Discussion Questions?',
    answer: 'Discussion questions can be used flexibly throughout a lesson. They may be used at the start of class to activate prior knowledge, during instruction to deepen understanding, or after instruction to assess comprehension. Students may respond verbally, in pairs, or as a whole class.',
  },
  {
    question: 'How is the Discussion Question Generator different from the Lesson Starter?',
    answer: 'The Lesson Starter introduces the topic and explains why it matters, ending with one open-ended question designed for a 5-minute discussion. The Discussion Question Generator creates standalone questions that do not introduce topics or explain why lessons matter. They complement each other rather than duplicating content.',
  },
  {
    question: 'What does the Learning Objectives Generator do?',
    answer: 'The Learning Objectives Generator creates clear, measurable learning objectives that define what students should be able to do by the end of a lesson. These objectives guide instruction and help keep lessons focused and aligned.',
  },
  {
    question: 'When should learning objectives be shared with students?',
    answer: 'Learning objectives are often shared at the beginning of class and revisited during or at the end of the lesson. Teachers may display them, discuss them briefly, or use them to frame activities and assessments.',
  },
  {
    question: 'How do I generate content?',
    answer: 'Navigate to any generator from the dashboard or sidebar, fill in the required fields like topic and grade level, then click "Generate". Your content will be created using AI and displayed for you to copy, download, or save.',
  },
  {
    question: 'What counts as a generation?',
    answer: 'Each time you create new content using any of our AI generators, it counts as one generation. Editing or copying existing content does not use generations.',
  },
  {
    question: 'Can I upgrade or downgrade my plan?',
    answer: 'Yes! You can change your plan at any time from the Billing page. Upgrades take effect immediately, and downgrades take effect at the end of your current billing period.',
  },
  {
    question: 'How do I download my content?',
    answer: 'After generating content, you\'ll see download buttons for Word and PDF formats. All plans including the free trial have access to downloads.',
  },
  {
    question: 'How do I cancel my subscription?',
    answer: 'You can cancel anytime from the Billing page. Your access continues until the end of your current billing period. We offer a 30-day money-back guarantee for all paid plans.',
  },
];

export default function HelpSupport() {
  const navigate = useNavigate();

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

        <div className="space-y-6">
          {/* FAQ Section */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Frequently Asked Questions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible className="w-full">
                {faqs.map((faq, index) => (
                  <AccordionItem key={index} value={`item-${index}`}>
                    <AccordionTrigger className="text-left">
                      {faq.question}
                    </AccordionTrigger>
                    <AccordionContent className="text-muted-foreground">
                      {faq.answer}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>

          {/* Resources */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Additional Resources</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <a 
                href="/legal/terms-of-service" 
                className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
              >
                <span className="font-medium">Terms of Service</span>
                <ExternalLink className="h-4 w-4 text-muted-foreground" />
              </a>
              <a 
                href="/legal/privacy-policy" 
                className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
              >
                <span className="font-medium">Privacy Policy</span>
                <ExternalLink className="h-4 w-4 text-muted-foreground" />
              </a>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
