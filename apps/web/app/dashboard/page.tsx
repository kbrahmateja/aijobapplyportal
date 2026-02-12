import { ApplicationList } from "@/components/application-list";
import { UserButton } from "@clerk/nextjs";

export default function DashboardPage() {
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
            <header className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
                <UserButton afterSignOutUrl="/" />
            </header>

            <main className="max-w-4xl mx-auto space-y-8">
                <section>
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Placeholder stats - could be fetched from API later */}
                            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded">
                                <p className="text-sm text-gray-500">Total Applications</p>
                                <p className="text-2xl font-bold">--</p>
                            </div>
                            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded">
                                <p className="text-sm text-gray-500">Success Rate</p>
                                <p className="text-2xl font-bold">--%</p>
                            </div>
                            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded">
                                <p className="text-sm text-gray-500">Active Queues</p>
                                <p className="text-2xl font-bold">--</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <ApplicationList />
                </section>
            </main>
        </div>
    );
}
