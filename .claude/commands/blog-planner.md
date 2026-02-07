---
description: Plan engaging blog posts with topic research, structured outlines, headline variations, and compelling introductions. Use when user asks to plan, outline, or write blog content.
handoffs:
  - label: Generate Blog Plan
    prompt: Create a comprehensive blog post plan for the given topic and audience
    send: true
---

# Blog Planning Skill

## When to Use This Skill

- User asks to "plan a blog post" or "write an article"
- User mentions blog topics, headlines, or content strategy
- User needs help structuring written content

## Procedure

1. **Understand the topic**: Clarify subject and target audience
2. **Create outline**: Structure into 3-5 main sections
3. **Generate headlines**: Provide 5 variations (curiosity-driven, benefit-focused, direct)
4. **Draft introduction**: Write a hook that challenges assumptions or poses a question

## Output Format

**Topic Summary**: 2-3 sentence overview
**Target Audience**: Who should read this?
**Outline**: Numbered list of main sections with brief descriptions
**Headline Options**: 5 variations
**Introduction Draft**: 1-2 paragraph hook

## Quality Criteria

- Headlines: Curiosity-driven, NEVER clickbait
- Introductions: Under 100 words, challenge assumptions or pose unexpected questions
- Outlines: Problem → insight → application structure
- Specificity: Use numbers over vague claims ("30% improvement" not "significant gains")

## Example

**Input**: "Help me plan a blog post about sustainable living"

**Output**:
- **Topic Summary**: Practical sustainable living tips for busy professionals who want impact without lifestyle overhaul.
- **Target Audience**: Working adults seeking eco-friendly changes that fit their schedule.
- **Outline**:
  1. The problem with perfectionist sustainability approaches
  2. The insight: small changes compound over time
  3. Application: 5 simple swaps for immediate impact
- **Headlines**:
  1. "You Don't Need to Be Perfect to Live Sustainably"
  2. "5 Sustainable Swaps That Take Less Time Than Your Coffee Break"
  3. "Why Most Sustainability Advice Is Wrong (And What Works Instead)"
  4. "The Lazy Person's Guide to Environmental Impact"
  5. "Sustainable Living for People Who Don't Have Time for Sustainable Living"
- **Introduction**: "You've seen the Instagram influencers with their zero-waste pantries and composting systems. Here's what they don't show: most of those lifestyles require hours of maintenance. You can cut your environmental impact by 40% with changes that take less time than your morning scroll."

## Implementation

ARGUMENTS: $ARGUMENTS

## Processing

Based on the provided arguments, I will create a comprehensive blog post plan following the outlined procedure:

1. Analyze the topic and identify the target audience
2. Create a structured outline with 3-5 main sections
3. Generate 5 compelling headline variations
4. Draft an engaging introduction that hooks the reader