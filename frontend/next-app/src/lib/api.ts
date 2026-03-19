const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

// Since the backend uses "get_current_user" with a dummy or actual user, we'll
// mock a user authentication header for now if needed, though testing locally might just bypass it.
const defaultHeaders = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer test-token',
    // In a real app, you would add an Authorization header here.
};

export async function createProject(problemStatement: string) {
    const response = await fetch(`${API_BASE_URL}/projects`, {
        method: 'POST',
        headers: defaultHeaders,
        body: JSON.stringify({ problem_statement: problemStatement }),
    });

    if (!response.ok) {
        throw new Error('Failed to create project');
    }

    return response.json();
}

export async function getRecentProjects(limit: number = 10) {
    const response = await fetch(`${API_BASE_URL}/projects?limit=${limit}`, {
        method: 'GET',
        headers: defaultHeaders,
    });

    if (!response.ok) {
        throw new Error('Failed to fetch recent projects');
    }

    return response.json();
}

export async function getProject(projectId: string) {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        method: 'GET',
        headers: defaultHeaders,
    });

    if (!response.ok) {
        throw new Error(`Failed to get project ${projectId}`);
    }

    return response.json();
}

export async function runPhase(projectId: string, phaseName: string) {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/run-phase/${phaseName}`, {
        method: 'POST',
        headers: defaultHeaders,
    });

    if (!response.ok) {
        throw new Error(`Failed to run phase ${phaseName}`);
    }

    return response.json();
}

export async function getPhase(projectId: string, phaseName: string) {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/phase/${phaseName}`, {
        method: 'GET',
        headers: defaultHeaders,
    });

    if (!response.ok) {
        if (response.status === 404) return null; // Phase might not exist yet
        throw new Error(`Failed to get phase ${phaseName}`);
    }

    return response.json();
}

export async function updatePhase(projectId: string, phaseName: string, humanApprovedData: any) {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/phase/${phaseName}`, {
        method: 'PUT',
        headers: defaultHeaders,
        body: JSON.stringify({ human_approved_data: humanApprovedData }),
    });

    if (!response.ok) {
        throw new Error(`Failed to update phase ${phaseName}`);
    }

    return response.json();
}
