// Membership Tiers
export const MEMBERSHIP_TIERS = {
  TRIAL: {
    name: "7-Day Trial",
    generations: 10,
    price: { monthly: 0, yearly: 0 },
    features: [
      "10 generations",
      "Word Downloads",
    ],
  },
  PRO: {
    name: "Pro",
    generations: -1, // -1 means unlimited
    price: { monthly: 25, yearly: 250 },
    features: [
      "Unlimited generations",
      "Word Downloads",
      "Save & Manage Content in Dashboard",
      "Priority Support",
      "Early Access to New Tools",
      "Food Science Academy Membership",
    ],
  },
} as const;

// Topic Categories
export const TOPIC_CATEGORIES = [
  { value: "food-chemistry", label: "Food Chemistry" },
  { value: "food-microbiology", label: "Food Microbiology" },
  { value: "food-safety", label: "Food Safety" },
  { value: "food-processing", label: "Food Processing & Preservation" },
  { value: "nutrition", label: "Nutrition" },
  { value: "culinary-science", label: "Culinary Science" },
  { value: "sensory-evaluation", label: "Sensory Evaluation" },
  { value: "food-careers", label: "Food Science Careers" },
  { value: "product-development", label: "Product Development" },
  { value: "other", label: "Other" },
] as const;

// Grade Levels
export const GRADE_LEVELS = [
  { value: "elementary", label: "Elementary" },
  { value: "middle", label: "Middle School" },
  { value: "high", label: "High School" },
  { value: "college", label: "College" },
] as const;

// Assessment Types
export const ASSESSMENT_TYPES = [
  { value: "multiple-choice", label: "Multiple Choice" },
  { value: "fill-blank", label: "Fill-in-the-Blank" },
  { value: "short-answer", label: "Short Answer" },
  { value: "true-false", label: "True/False" },
  { value: "matching", label: "Matching" },
  { value: "written-response", label: "Written Response" },
  { value: "mixed", label: "Mixed" },
] as const;

