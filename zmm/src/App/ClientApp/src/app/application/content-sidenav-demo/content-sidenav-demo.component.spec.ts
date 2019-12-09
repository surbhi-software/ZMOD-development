import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContentSidenavDemoComponent } from './content-sidenav-demo.component';

describe('ContentSidenavDemoComponent', () => {
  let component: ContentSidenavDemoComponent;
  let fixture: ComponentFixture<ContentSidenavDemoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ContentSidenavDemoComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ContentSidenavDemoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
