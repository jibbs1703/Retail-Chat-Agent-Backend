In this article, we will create a crew of AI Agents using crewai python sdk to perform literature review for academic research.

crewai
CrewAI is an open-source Python framework designed to orchestrate collaborative, role-based AI agents for complex task execution.

You can create autonomous agents with distinct roles, goals, and backstories, which work together in a structured workflow, or “crew,” to achieve objectives like research, summarization, or data analysis.
Prominent Abstractions in crewai
Crew: Top-level organization. Organizes the overall operation. Manages AI agent teams, oversees workflows, ensures collaboration, Delivers outcomes.
Agents: Specialized team members,Have specific roles, use designated Tools, can delegate tasks, make autonomous decisions
Process: Workflow management system, ensures smooth collaboration by defining collaboration patterns, Controls task assignments, Manages interactions, ensures efficient execution
Tasks: Individual assignments, they have cbjectives, use specific tools, feed into larger process, produce actional results.Tasks get completed to achieve the goal
Key Functionality in crewai
Enables creation of multiagent crews, agent collaboration and orchestration.
Handles multi-agent orchestration by defining specialized agents, assigning tasks with clear dependencies, and managing execution through sequential or hierarchical processes. It coordinates tools, memory, and outputs, ensuring collaborative task completion.
Agents are designed to focus on specific tasks and CrewAI coordinates their interactions based on their roles. The framework ensures agents operate within their defined scope while sharing context as needed.
Ensures tasks are executed in the correct order, passing relevant outputs between agents.
Orchestrates tool usage by managing inputs/outputs and ensuring tools are called appropriately during task execution.
Uses an internal event bus to manage events like task start/completion (CrewKickoffStartedEvent, etc.), coordinating agent actions. The event bus triggers actions (e.g., starting a task, passing outputs), ensuring smooth agent collaboration.
Aggregates task outputs into a final result, combining contributions from all agents. The framework ensures that the final output reflects the collaborative effort, formatted as specified.
Supports sequential, hierarchical, conditional and asynchronous execution (Process) of agents in a crew.
Sequential tasks are executed one after another, with each task’s output feeding into the next.
For hierarchical processes, a manager agent assigns tasks to worker agents dynamically, prioritizing tasks based on context or performance.
crewai supports three memory types — short term (single session), long term (vector DB), entity memory (reference specific agents or task).
You can develop multiple types of customized agents — coding agents, multimodal agent, agents witl complex hierarchical workflows.
You can build crews with human in the loop and other workflow control mechanisms
Supports custom LLMs, such as Groq’s Llama3 models, Hugging Face models, Ollama models besides all prominent providers.
How to choose an LLM for your crew

understand your task
see model features
account for your constraints
test and repeat
Let us build our multi-agent literature review agent crew:
Structure of our AI Agent crew:
Agents in the crew:
Literature Review Agent
Data Analyst Agent
Writer Agent
Citation Agent
Peer Review Agent
Tasks for our Agents:
Literature Review Task
Data Analysis Task
Writing Task
Citation Task
Peer Review Task
Press enter or click to view image in full size

Our Academic Literature Review MultiAgent Crew
First, you should have installed python and basic libraries for ML and datascience. Anaconda Python will be great. Then we need to install crewai.
Use following two command to install crewai and crewai-tools:

pip install crewai crewai-tools
2. I am using LLaMA3–70B model froom groq.com in this notebook as LLM brain for my research agents. You can use any other strong reasoning model or multiple models.

Become a member
If you also decide to use groq.com, you will need a GROQ API Key. Get your free key at https://groq.com/

Once you have installed crewai and obtained GROQ API Key we can code the multiagent system.

3. Let us define our five agents first:

# Define Agents
literature_review_agent = Agent(
    role="Literature Review Agent",
    goal="Search academic databases and summarize relevant papers on {research_topic}",
    backstory="You are an expert researcher skilled at navigating academic databases. "
              "Your role is to find and summarize high-quality, peer-reviewed papers "
              "relevant to the research topic, ensuring a comprehensive literature review.",
    allow_delegation=False,
    llm=groq_llm,
    verbose=True
)
data_analyst_agent = Agent(
    role="Data Analyst Agent",
    goal="Process and analyze research data for {research_topic}, generating statistical insights",
    backstory="You are a data scientist proficient in statistical analysis and data visualization. "
              "You analyze provided datasets or simulated data to uncover insights and trends "
              "relevant to the research topic, ensuring robust and reproducible results.",
    allow_delegation=False,
    llm=groq_llm,
    #tools=[SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))],
    #memory=True,
    # respect_context_window=True,
    verbose=True
)
writer_agent = Agent(
    role="Writer Agent",
    goal="Draft sections of a research paper on {research_topic} with clarity and academic rigor",
    backstory="You are an academic writer experienced in crafting research papers. "
              "You use inputs from the Literature Review and Data Analyst agents to write "
              "clear, concise, and well-structured paper sections adhering to academic standards.",
    allow_delegation=False,
    llm=groq_llm,
    verbose=True
)
citation_agent = Agent(
    role="Citation Agent",
    goal="Format references and ensure compliance with {citation_style} style for {research_topic}",
    backstory="You are a meticulous librarian specializing in citation management. "
              "You format references from the literature review and ensure all citations "
              "comply with the specified citation style (e.g., APA, MLA).",
    allow_delegation=False,
    llm=groq_llm,
    verbose=True
)
peer_review_agent = Agent(
    role="Peer Review Agent",
    goal="Simulate peer review to check logical consistency and identify gaps in the research paper on {research_topic}",
    backstory="You are an academic reviewer with a critical eye for detail. "
              "You evaluate the draft research paper for logical consistency, methodological rigor, "
              "and completeness, providing constructive feedback to improve the manuscript.",
    allow_delegation=False,
    llm=groq_llm,
    verbose=True
)
4. Now, let us define the five tasks and bind them to corresponding agents:

literature_review_task = Task(
    description=(
        "1. Search academic databases (e.g., Google Scholar, PubMed) for peer-reviewed papers on {research_topic}.\n"
        "2. Select 5 high-quality, relevant papers published within the last 5 years.\n"
        "3. Summarize each paper, highlighting key findings, methodologies, and gaps in the research.\n"
        "4. Provide a synthesis of the literature to guide the research paper."
    ),
    expected_output="A detailed literature review document in markdown format, including summaries of 5 papers and a synthesis section.",
    agent=literature_review_agent
)

data_analysis_task = Task(
    description=(
        "1. Analyze provided or simulated research data relevant to {research_topic}.\n"
        "2. Perform statistical analysis (e.g., descriptive statistics, regression, or hypothesis testing) as appropriate.\n"
        "3. Generate insights and, if applicable, describe visualizations (e.g., tables, charts) to support findings.\n"
        "4. Summarize results in a clear, academic format suitable for a research paper."
    ),
    expected_output="A data analysis report in markdown format, including statistical insights and descriptions of visualizations (if applicable).",
    agent=data_analyst_agent
)

writing_task = Task(
    description=(
        "1. Use the literature review and data analysis reports to draft sections of a research paper on {research_topic}.\n"
        "2. Include an introduction, literature review summary, methodology, results, and discussion sections.\n"
        "3. Ensure clarity, academic tone, and adherence to scholarly standards.\n"
        "4. Structure the paper with appropriate headings and subheadings."
    ),
    expected_output="A draft research paper in markdown format with introduction, literature review, methodology, results, and discussion sections.",
    agent=writer_agent
)


citation_task = Task(
    description=(
        "1. Collect references from the literature review and any additional sources used in the paper.\n"
        "2. Format all references according to the {citation_style} style (e.g., APA, MLA).\n"
        "3. Ensure in-text citations and the reference list are complete and correctly formatted."
    ),
    expected_output="A formatted reference list in markdown format, compliant with {citation_style}, and in-text citation guidelines.",
    agent=citation_agent
)

peer_review_task = Task(
    description=(
        "1. Review the draft research paper for logical consistency, methodological rigor, and completeness.\n"
        "2. Identify gaps, unclear arguments, or areas needing further evidence or clarification.\n"
        "3. Provide constructive feedback and suggestions for improvement in a concise report."
    ),
    expected_output="A peer review report in markdown format, detailing feedback, identified gaps, and improvement suggestions.",
    agent=peer_review_agent
)
5. Now, create a crew by instantiating Crew() class. We provide it the list of agents and tasks.

from crewai import Process
# Create the Crew
research_crew = Crew(
    agents=[
        literature_review_agent,
        data_analyst_agent,
        writer_agent,
        citation_agent,
        peer_review_agent
    ],
    tasks=[
        literature_review_task,
        data_analysis_task,
        writing_task,
        citation_task,
        peer_review_task
    ],
    process=Process.sequential,  # Tasks run sequentially
    verbose=True
)
6. Next, we set the crew working by providing it a topic of research and a citation style we wish our citations in. This is done by invoking kickoff() method on your crew object.

# Kickoff the crew with inputs
result = research_crew.kickoff(inputs={"research_topic": "Machine Learning in Healthcare", "citation_style": "APA"})
7. Above command makes your agents run in correct order (sequential, in our case) and you get the final results of research review in markdown format. To display that markdown use below code:

# Display results as markdown
markdown_content = result.raw
from IPython.display import Markdown
Markdown(markdown_content)
8. You can save your markdown to a word file using below code:

import markdown
import pdfkit
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.style import WD_STYLE_TYPE
from datetime import datetime
import os
import re

# Save markdown as Word (.docx)
def save_markdown_to_docx(markdown_text, output_file="research_paper.docx", research_topic="Machine Learning in Healthcare"):
    # Convert markdown to HTML for intermediate processing
    html_content = markdown.markdown(markdown_text, extensions=['extra', 'toc', 'tables'])

    # Create a new Word document
    doc = Document()

    # Define custom styles
    styles = doc.styles
    heading_style = styles.add_style('CustomHeading', WD_STYLE_TYPE.PARAGRAPH)
    heading_style.font.name = 'Times New Roman'
    heading_style.font.size = Pt(14)
    heading_style.font.bold = True

    body_style = styles.add_style('CustomBody', WD_STYLE_TYPE.PARAGRAPH)
    body_style.font.name = 'Times New Roman'
    body_style.font.size = Pt(12)

    # Add cover page
    doc.add_heading(research_topic, 0)
    doc.add_paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", style='CustomBody')
    doc.add_paragraph("Prepared by Academic Research Crew", style='CustomBody')
    doc.add_page_break()

    # Parse HTML to add content to Word document
    table_data = []
    in_table = False
    for line in html_content.split('\n'):
        if line.startswith('<h1>'):
            doc.add_heading(line.replace('<h1>', '').replace('</h1>', ''), level=1).style = heading_style
        elif line.startswith('<h2>'):
            doc.add_heading(line.replace('<h2>', '').replace('</h2>', ''), level=2).style = heading_style
        elif line.startswith('<p>'):
            doc.add_paragraph(line.replace('<p>', '').replace('</p>', ''), style=body_style)
        elif line.startswith('<li>'):
            doc.add_paragraph(line.replace('<li>', '').replace('</li>', ''), style='ListBullet')
        elif line.startswith('<table>'):
            in_table = True
            table_data = []
        elif line.startswith('</table>'):
            in_table = False
            # Create table in Word
            if table_data:
                rows = len(table_data)
                cols = len(table_data[0])
                table = doc.add_table(rows=rows, cols=cols)
                table.style = 'Table Grid'
                for i, row_data in enumerate(table_data):
                    for j, cell_text in enumerate(row_data):
                        table.cell(i, j).text = cell_text
        elif in_table and line.startswith('<tr>'):
            table_data.append([])
        elif in_table and line.startswith('<td>'):
            table_data[-1].append(line.replace('<td>', '').replace('</td>', ''))
        else:
            # Add other content as paragraphs
            if line.strip() and not any(tag in line for tag in ['<h', '<p', '<li', '<table', '<tr', '<td']):
                doc.add_paragraph(line, style=body_style)

    # Save the document
    doc.save(output_file)
    print(f"Word document saved as {output_file}")

save_markdown_to_docx(markdown_content, "research_paper.docx", research_topic="Machine Learning in Healthcare")

There you go, you just created your own multi-agent AI crew to help you with academic literature review.
