// github_api.js — Thin wrapper around the GitHub REST API

const GITHUB_API = 'https://api.github.com';

async function githubRequest(path, token, options = {}) {
  const res = await fetch(`${GITHUB_API}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || `GitHub API error ${res.status}`);
  }

  return res.status === 204 ? null : res.json();
}

// Submit a pull request review.
// event: 'APPROVE' | 'REQUEST_CHANGES' | 'COMMENT'
// body:  string shown as the review comment
async function submitReview({ owner, repo, pullNumber, token, event, body }) {
  return githubRequest(
    `/repos/${owner}/${repo}/pulls/${pullNumber}/reviews`,
    token,
    {
      method: 'POST',
      body: JSON.stringify({ event, body }),
    }
  );
}

// Fetch the authenticated user's login (used to verify the token is valid).
async function getAuthenticatedUser(token) {
  return githubRequest('/user', token);
}
