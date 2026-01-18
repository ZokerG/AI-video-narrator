"use client";

export default function DebugAuthPage() {
    const checkAuth = () => {
        const token = localStorage.getItem("auth_token");
        const user = localStorage.getItem("auth_user");

        console.log("=== AUTH DEBUG ===");
        console.log("Token exists:", !!token);
        console.log("Token value:", token);
        console.log("User exists:", !!user);
        console.log("User value:", user);

        if (token) {
            // Test API call
            fetch("http://localhost:8000/auth/me", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            })
                .then(res => res.json())
                .then(data => {
                    console.log("API Response:", data);
                    alert(`Auth works! User: ${JSON.stringify(data)}`);
                })
                .catch(err => {
                    console.error("API Error:", err);
                    alert(`Auth failed: ${err.message}`);
                });
        } else {
            alert("No token found in localStorage!");
        }
    };

    return (
        <div className="p-8">
            <h1 className="text-2xl font-bold mb-4">Auth Debug</h1>
            <button
                onClick={checkAuth}
                className="px-4 py-2 bg-blue-600 text-white rounded"
            >
                Check Auth
            </button>

            <div className="mt-4 text-gray-600">
                <p>Open browser console (F12) to see results</p>
            </div>
        </div>
    );
}
