import React, { FC } from 'react';
import { Trajectory } from '../../models/trajectory'; // Assuming '@models' alias is configured
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'; // Assuming '@components' alias
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the copy button

// Define the specific type for this trajectory variant
type UserQueryTrajectoryModel = Extract<Trajectory, { recordType: 'user_query' }>;

interface UserQueryTrajectoryProps {
  trajectory: UserQueryTrajectoryModel;
}

/**
 * Renders a trajectory step representing the initial user query that started the session.
 */
export const UserQueryTrajectory: FC<UserQueryTrajectoryProps> = ({ trajectory }) => {
  // Safely access the query from stepData. Use empty string for copy button if query is missing.
  const query = trajectory.stepData?.query ?? '';
  const displayQuery = query || 'Initial query data not available.'; // Fallback for display

  return (
    <Card className="mb-4 border-blue-200 bg-blue-50 shadow-sm"> {/* Subtle blue theme */}
      <CardHeader className="pb-2 pt-3 flex flex-row justify-between items-center"> {/* Use flexbox for layout */}
        <CardTitle className="text-sm font-semibold text-blue-800"> {/* Styled title */}
          Initial User Input
        </CardTitle>
        {/* Add the copy button, passing the potentially empty query */}
        <CopyToClipboardButton textToCopy={query} className="h-6 w-6 p-0.5" /> {/* Pass query and optional styling */}
      </CardHeader>
      <CardContent className="pb-3"> {/* Compact content padding */}
        {/* Use pre-wrap to preserve whitespace and line breaks from the original query */}
        <p className="whitespace-pre-wrap text-sm text-gray-800">{displayQuery}</p>
      </CardContent>
    </Card>
  );
};
