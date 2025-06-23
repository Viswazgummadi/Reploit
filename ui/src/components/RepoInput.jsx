// A loading spinner component for our button
const Spinner = () => (
  <svg
    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    ></circle>
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    ></path>
  </svg>
);

// The main input component
const RepoInput = ({ repoUrl, setRepoUrl, handleIndexRepo, isIndexing }) => {
  return (
    <div className="p-8 border border-gray-700 rounded-lg bg-gray-800/50 shadow-lg backdrop-blur-sm">
      <form
        onSubmit={(e) => {
          e.preventDefault(); // Prevent page refresh on form submission
          handleIndexRepo();
        }}
      >
        <label
          htmlFor="repo-url"
          className="block text-lg font-medium text-gray-300"
        >
          GitHub Repository URL
        </label>
        <p className="text-sm text-gray-500 mt-1 mb-4">
          Enter the URL of a public repository you wish to analyze. The initial
          analysis may take several minutes.
        </p>
        <div className="flex items-center space-x-4">
          <input
            id="repo-url"
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/user/repo"
            className="flex-grow bg-gray-900 border border-gray-600 rounded-md px-4 py-2 text-white focus:ring-2 focus:ring-teal-400 focus:outline-none transition-colors"
            disabled={isIndexing}
          />
          <button
            type="submit"
            disabled={isIndexing || !repoUrl}
            className="flex items-center justify-center bg-teal-500 hover:bg-teal-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-2 px-6 rounded-md transition-colors duration-200"
          >
            {isIndexing ? <Spinner /> : null}
            {isIndexing ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RepoInput;
