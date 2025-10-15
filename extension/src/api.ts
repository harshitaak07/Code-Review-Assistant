import axios from "axios";

const BACKEND_URL = "http://localhost:5000";

export async function submitCode(code: string): Promise<number> {
  const res = await axios.post(`${BACKEND_URL}/submit-code`, { code });
  return res.data.submission_id;
}

export async function getFeedback(submissionId: number): Promise<any> {
  while (true) {
    const res = await axios.get(`${BACKEND_URL}/get-feedback/${submissionId}`);
    if (res.data.status === "done") {
      return res.data.feedback;
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
}
