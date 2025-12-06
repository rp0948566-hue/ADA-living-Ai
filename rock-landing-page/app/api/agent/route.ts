
import { type NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  console.log('Received message from frontend:', body.message);
  return NextResponse.json({ reply: 'Message received by the agent!' });
}
