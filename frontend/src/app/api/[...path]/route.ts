
import { NextRequest, NextResponse } from "next/server";

// This is the internal Docker URL or the public URL if not in Docker logic
// When running in Docker, "backend" resolves to the backend service.
const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || "http://backend:8000";

async function proxyRequest(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
    // Await params as per Next.js 15+ requirements
    const resolvedParams = await params;

    // Construct the backend URL
    const path = resolvedParams.path.join("/");
    const query = request.nextUrl.search;
    const targetUrl = `${BACKEND_URL}/${path}${query}`;

    console.log(`[Proxy] Forwarding ${request.method} ${request.nextUrl.pathname} -> ${targetUrl}`);

    try {
        const headers = new Headers(request.headers);
        // Remove host header to avoid confusion at backend
        headers.delete("host");

        // Forward the request
        const response = await fetch(targetUrl, {
            method: request.method,
            headers: headers,
            body: request.body,
            // Important for some streaming/upload cases
            duplex: "half",
        } as any);

        // Forward the response back to client
        return new NextResponse(response.body, {
            status: response.status,
            headers: response.headers,
        });

    } catch (error) {
        console.error("[Proxy Error]", error);
        return NextResponse.json({ error: "Backend unreachable" }, { status: 502 });
    }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;
export const PATCH = proxyRequest;
