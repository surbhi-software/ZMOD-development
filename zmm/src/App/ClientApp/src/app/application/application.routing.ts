import { ModuleWithProviders } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ApplicationComponent } from './application.component';
import { UsersComponent } from './users/users.component';
import { DataComponent } from './data/data.component';
import { EditorComponent } from './editor/editor.component';
import { ProfileComponent } from './profile/profile.component';
import { ModelsComponent } from './models/models.component';
import { CodeComponent } from './code/code.component';
import { ContentSidenavDemoComponent } from './content-sidenav-demo/content-sidenav-demo.component';
import { TasksComponent } from './tasks/tasks.component';
import { AssetsComponent } from './assets/assets.component';
import { LicenseComponent } from './license/license.component';
import { RepoComponent } from './repo/repo.component';
import { SettingsComponent } from './settings/settings.component';

const MAIN_ROUTES: Routes = [
    {
        path: '', component: ApplicationComponent, children: [
            { path: '', redirectTo: 'data', pathMatch: 'full' },
            { path: 'users', component: UsersComponent },
            { path: 'data', component: DataComponent },
            { path: 'code', component: CodeComponent },
            { path: 'models', component: ModelsComponent },
            { path: 'editor', component: EditorComponent },
            { path: 'profile', component: ProfileComponent },
            { path: 'demo', component: ContentSidenavDemoComponent },
            { path: 'tasks', component: TasksComponent },
            { path: 'assets', component: AssetsComponent },
            { path: 'license', component: LicenseComponent },
            { path: 'repo', component: RepoComponent},
            { path: 'settings', component: SettingsComponent },
            { path: '**', redirectTo: 'data' }
        ]
    }
];

export const ApplicationRouting: ModuleWithProviders = RouterModule.forChild(MAIN_ROUTES);
